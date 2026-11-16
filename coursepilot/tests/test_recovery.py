import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from coursepilot.engine import Session,HERE
from coursepilot.providers import ClaudeProvider,ProviderError,parse_claude_output
from coursepilot.recovery import recover_saved_draft
from evaluation.providers import write_json


RAW=(Path(__file__).parent/'fixtures/claude_corrected_draft.jsonl').read_text(encoding='utf-8')
SCHEMA=json.loads((HERE/'schemas/agent.json').read_text(encoding='utf-8'))


class RecoveryTests(unittest.TestCase):
    def test_corrected_schema_response_accepts_only_proven_unavailable_course_attempt(self):
        value,metadata,_=parse_claude_output(RAW,SCHEMA,'test')
        self.assertEqual('draft_plan',value['tool'])
        self.assertEqual(['90001','90002','90006','90010'],value['sections'])
        self.assertEqual([{'name':'draft_plan','id':'unavailable-draft'}],metadata['unavailable_course_tool_attempts'])

    def test_actual_available_native_tool_is_still_rejected(self):
        raw=RAW.replace('"tools":["StructuredOutput"]','"tools":["StructuredOutput","draft_plan"]')
        with self.assertRaisesRegex(ProviderError,'not proven unavailable'):parse_claude_output(raw,SCHEMA,'test')

    def test_attempt_without_matching_tool_error_is_rejected(self):
        raw='\n'.join(line for line in RAW.splitlines() if 'No such tool available' not in line)
        with self.assertRaisesRegex(ProviderError,'not proven unavailable'):parse_claude_output(raw,SCHEMA,'test')

    def stopped_run(self,root):
        with patch('coursepilot.providers.shutil.which',return_value='claude'),patch('coursepilot.providers.subprocess.run',return_value=subprocess.CompletedProcess([],0,'test-cli','')):
            provider=ClaudeProvider(Path(root)/'transport')
        s=Session(root,provider=provider,mode='human',case_path=HERE/'cases/hudson_b.json')
        s.student(s.steps[0]['message'],stage=0,auto_start=False)
        s.env.tool('draft_plan','Plan A',['90001','90002','90004','90010'])
        s.student(s.steps[1]['message'],stage=1,auto_start=False)
        s.status='error';s.error='ProviderError: Native Claude tool draft_plan was used'
        prompt=json.dumps({'instructions':'test','conversation':s.history})
        s.record('model_request','agent',prompt=prompt)
        s.record('model_error','agent',error=s.error,raw_provider_events=[json.loads(line) for line in RAW.splitlines()])
        s.record('error','runner',error=s.error)
        s.persist()
        p=s.output/'provider';p.mkdir()
        write_json(p/'agent-001.request.json',{'prompt':prompt,'schema':SCHEMA})
        (p/'agent-001.events.jsonl').write_text(RAW,encoding='utf-8')
        return s

    def test_interactive_recovery_uses_no_inference_and_preserves_original_error(self):
        with tempfile.TemporaryDirectory() as root:
            source=self.stopped_run(root)
            original=(source.output/'config.json').read_bytes()
            with patch('subprocess.run',side_effect=AssertionError('Recovery must not invoke a model')):
                recovered=recover_saved_draft(source.output)
            self.assertEqual(1,recovered.metrics()['task_success'])
            self.assertEqual(2,recovered.metrics()['user_turns'])
            self.assertEqual('awaiting_student',recovered.status)
            self.assertEqual(original,(source.output/'before-recovery/config.json').read_bytes())
            self.assertEqual(RAW,(source.output/'provider/agent-001.events.jsonl').read_text(encoding='utf-8'))
            self.assertFalse(recovered.continuation['new_model_inference'])
            recovered.finish()
            self.assertTrue(json.loads((source.output/'config.json').read_text())['finalized'])

    def test_finalized_evidence_cannot_be_recovered_or_rewritten(self):
        with tempfile.TemporaryDirectory() as root:
            source=self.stopped_run(root);source.finish()
            before=(source.output/'config.json').read_bytes()
            with self.assertRaisesRegex(ValueError,'unfinished'):recover_saved_draft(source.output)
            self.assertEqual(before,(source.output/'config.json').read_bytes())
