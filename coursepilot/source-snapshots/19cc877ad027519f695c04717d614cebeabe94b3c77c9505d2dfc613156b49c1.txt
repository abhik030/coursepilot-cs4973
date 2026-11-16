"""Transport boundaries: malformed/error output never becomes a course action."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from coursepilot.engine import Session, HERE
from coursepilot.providers import ClaudeProvider, ProviderError, make_provider, model_for
from coursepilot.server import App


VALUE = {'message': 'Ready', 'intent': 'chat', 'target': ''}


def events(**result):
    return [{'type': 'system', 'subtype': 'init', 'model': 'claude-test-model'},
            {'type': 'assistant', 'message': {'model': 'claude-test-model', 'content':
             [{'type': 'tool_use', 'name': 'StructuredOutput', 'input': VALUE}]}},
            {'type': 'result', 'subtype': 'success', 'is_error': False,
             'structured_output': VALUE, 'usage': {'input_tokens': 10, 'output_tokens': 5,
             'cache_creation_input_tokens': 20, 'cache_read_input_tokens': 30}, **result}]


class ClaudeTransportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)
        with patch('coursepilot.providers.shutil.which', return_value='claude'), \
             patch('coursepilot.providers.subprocess.run', return_value=subprocess.CompletedProcess([], 0, '2.1.test', '')):
            self.provider = ClaudeProvider(self.folder)

    def invoke(self, stream=None, returncode=0):
        self.raw = '\n'.join(json.dumps(e) for e in (stream if stream is not None else events()))+'\n'
        result = subprocess.CompletedProcess([], returncode, self.raw, '')
        with patch('coursepilot.providers.subprocess.run', return_value=result) as call:
            value, metadata = self.provider.complete('user', 'Prompt', HERE/'schemas/user.json')
        return value, metadata, call.call_args

    def test_schema_result_preserves_raw_evidence_and_normalizes_usage(self):
        value, meta, call = self.invoke()
        self.assertEqual(VALUE, value)
        self.assertEqual({'input_tokens': 60, 'output_tokens': 5}, meta['usage'])
        self.assertEqual(self.raw, (self.folder/'user-001.events.jsonl').read_text(encoding='utf-8'))
        self.assertEqual(VALUE, json.loads((self.folder/'user-001.response.json').read_text()))
        self.assertEqual(['claude-test-model'], self.provider.describe()['resolved_models'])
        command=call.args[0]
        self.assertEqual('', command[command.index('--tools')+1])
        self.assertIn('--strict-mcp-config', command)
        self.assertIn('--safe-mode', command)
        self.assertIn('--no-session-persistence', command)
        self.assertNotIn('shell', call.kwargs)

    def test_native_tool_cannot_be_hidden_by_a_valid_final_result(self):
        stream=events()
        stream[1]['message']['content'].insert(0, {'type':'tool_use','name':'Bash','input':{'command':'anything'}})
        with self.assertRaisesRegex(ProviderError, 'Native Claude tool Bash'):
            self.invoke(stream)
        self.assertFalse((self.folder/'user-001.response.json').exists())

    def test_denied_tool_attempt_is_rejected(self):
        with self.assertRaisesRegex(ProviderError, 'denied native tool'):
            self.invoke(events(permission_denials=[{'tool_name':'Read'}]))

    def test_error_result_does_not_use_structured_payload(self):
        with self.assertRaisesRegex(ProviderError, 'did not complete'):
            self.invoke(events(is_error=True, subtype='error_max_turns'))

    def test_missing_structured_output_does_not_parse_freeform_text(self):
        with self.assertRaisesRegex(ProviderError, 'no structured response'):
            self.invoke(events(structured_output=None, result=json.dumps(VALUE)))

    def test_malformed_stream_is_retained_and_rejected(self):
        with patch('coursepilot.providers.subprocess.run', return_value=subprocess.CompletedProcess([],0,'bad json','')):
            with self.assertRaisesRegex(ProviderError, 'non-JSON'):
                self.provider.complete('user','Prompt',HERE/'schemas/user.json')
        self.assertEqual('bad json',(self.folder/'user-001.events.jsonl').read_text())

    def test_expired_authentication_has_actionable_error(self):
        with self.assertRaisesRegex(ProviderError, 'claude auth login'):
            self.invoke([{'type':'assistant','error':'authentication_failed'}],returncode=1)

    def test_timeout_preserves_partial_utf8_output(self):
        with patch('coursepilot.providers.subprocess.run', side_effect=subprocess.TimeoutExpired('claude',120,output=b'partial',stderr=b'timeout')):
            with self.assertRaisesRegex(ProviderError, 'timed out'):
                self.provider.complete('user','Prompt',HERE/'schemas/user.json')
        self.assertEqual('partial',(self.folder/'user-001.events.jsonl').read_text())


class ProviderRoutingTests(unittest.TestCase):
    def test_factory_uses_provider_specific_defaults_without_fallback(self):
        with patch('coursepilot.providers.CodexProvider') as codex, patch('coursepilot.providers.ClaudeProvider') as claude:
            make_provider('codex','out')
            make_provider('claude','out')
            codex.assert_called_once_with('out','gpt-6.1-sol','medium',120)
            claude.assert_called_once_with('out','sonnet','medium',120)
        with self.assertRaises(ValueError): model_for('unknown')

    def test_browser_provider_override_does_not_inherit_other_providers_model(self):
        with tempfile.TemporaryDirectory() as root, patch('coursepilot.server.Session') as session:
            session.return_value.id='test'
            app=App(root,'gpt-6.1-sol','medium',provider_name='codex')
            app.create({'provider':'claude','mode':'human'})
            self.assertEqual('sonnet',session.call_args.args[3])
            self.assertEqual('claude',session.call_args.kwargs['provider_name'])
            with self.assertRaises(ValueError):app.create({'provider':'invalid'})

    def test_real_transport_type_is_identified_in_run_config(self):
        with tempfile.TemporaryDirectory() as root:
            transport=ClaudeProvider.__new__(ClaudeProvider)
            transport.describe=lambda: {'provider':'claude-code','model_version':'test-sonnet'}
            session=Session(root,provider=transport)
            config=json.loads((session.output/'config.json').read_text())
            self.assertEqual('llm_evaluation',config['evidence_kind'])
            self.assertEqual('claude-code',config['agent_model']['provider'])
