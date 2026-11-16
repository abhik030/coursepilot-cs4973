"""Interchangeable local CLI inference; course actions stay in the Python harness."""
from pathlib import Path
import json
import shutil
import subprocess
import time

from evaluation.providers import CodexProvider, ProviderError, utc_now, write_json

DEFAULT_MODELS = {'codex': 'gpt-6.1-sol', 'claude': 'sonnet'}


def provider_options():
    return [{'id': name, 'label': label, 'default_model': DEFAULT_MODELS[name],
             'available': shutil.which(name) is not None}
            for name, label in [('codex', 'Codex CLI'), ('claude', 'Claude Code')]]


def model_for(provider, model=None):
    if provider not in DEFAULT_MODELS:
        raise ValueError('Choose provider codex or claude.')
    if model is not None and (not isinstance(model, str) or not model.strip() or len(model) > 150):
        raise ValueError('Enter a model name of 1–150 characters.')
    return model.strip() if model else DEFAULT_MODELS[provider]


def make_provider(provider, output_dir, model=None, effort='medium', timeout=120):
    model = model_for(provider, model)
    cls = CodexProvider if provider == 'codex' else ClaudeProvider
    return cls(output_dir, model, effort, timeout)


def parse_claude_output(stdout,schema,stem):
    """Accept schema output after a proven-unavailable course-call correction."""
    events=[];attempts=[];models=set()
    course_tools=set(schema.get('properties',{}).get('tool',{}).get('enum',[]))-{'none'}
    for line in stdout.splitlines():
        if not line.strip():continue
        try:event=json.loads(line)
        except json.JSONDecodeError as exc:raise ProviderError(f'Unexpected non-JSON Claude output; preserved at {stem}') from exc
        if not isinstance(event,dict):raise ProviderError(f'Invalid Claude event; inspect {stem}')
        events.append(event)
        message=event.get('message') or {}
        model=message.get('model') or (event.get('model') if event.get('subtype')=='init' else None)
        if model and model!='<synthetic>':models.add(model)
        for block in message.get('content',[]):
            if block.get('type') in ('tool_use','server_tool_use') and block.get('name')!='StructuredOutput':
                if block.get('type')=='tool_use' and block.get('name') in course_tools:
                    attempts.append(block)
                else:raise ProviderError(f'Native Claude tool {block.get("name")} was used; raw events preserved at {stem}.')
        if event.get('type')=='error':raise ProviderError(f'Claude inference error; inspect {stem}')
    endings=[e for e in events if e.get('type')=='result']
    if len(endings)!=1 or endings[0].get('is_error') or endings[0].get('subtype')!='success':
        raise ProviderError(f'Claude did not complete successfully; inspect {stem}')
    final=endings[0];value=final.get('structured_output')
    if not isinstance(value,dict):raise ProviderError(f'Claude returned no structured response; inspect {stem}')
    if final.get('permission_denials'):raise ProviderError(f'Claude attempted a denied native tool; inspect {stem}')
    for attempt in attempts:
        init=next((e for e in events if e.get('type')=='system' and e.get('subtype')=='init'),{})
        unavailable=('tools' in init and set(init['tools'])<={'StructuredOutput'} and init.get('mcp_servers')==[])
        rejected=bool(attempt.get('id')) and any(block.get('type')=='tool_result' and block.get('tool_use_id')==attempt.get('id')
                     and block.get('is_error') is True and isinstance(block.get('content'),str)
                     and f'No such tool available: {attempt["name"]}' in block['content']
                     for e in events if e.get('type')=='user' for block in (e.get('message') or {}).get('content',[]))
        if not unavailable or not rejected:
            raise ProviderError(f'Native Claude tool {attempt["name"]} was not proven unavailable; inspect {stem}')
    usage=final.get('usage') or {}
    normalized={'input_tokens':sum(usage.get(k,0) or 0 for k in ('input_tokens','cache_creation_input_tokens','cache_read_input_tokens')),
                'output_tokens':usage.get('output_tokens',0) or 0}
    return value,{'events':events,'usage':normalized,'raw_usage':usage,
                  'unavailable_course_tool_attempts':[{'name':a['name'],'id':a.get('id')} for a in attempts]},models


class ClaudeProvider:
    """Fresh Claude Code print calls, with schema output and no native course tools."""

    def __init__(self, output_dir, model='sonnet', effort='medium', timeout=120):
        self.output_dir = Path(output_dir).resolve()
        self.model, self.effort, self.timeout = model, effort, timeout
        self.executable = shutil.which('claude')
        if not self.executable:
            raise ProviderError("Claude Code CLI was not found. Install it and run 'claude auth login', then retry.")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.workspace = self.output_dir / 'model-workspace'
        self.workspace.mkdir(exist_ok=True)
        self.calls = {'agent': 0, 'user': 0}
        self.resolved_models = set()
        self.version = subprocess.run([self.executable, '--version'], capture_output=True,
                                      text=True, encoding='utf-8', timeout=15).stdout.strip()

    def describe(self):
        return {'provider': 'claude-code', 'cli_version': self.version,
                'model_version': self.model, 'model_version_kind': 'requested_model_alias',
                'resolved_models': sorted(self.resolved_models), 'immutable_backend_snapshot': None,
                'version_note': 'Requested alias plus model identifiers observed in raw responses; no immutable backend snapshot is claimed.',
                'reasoning_effort': self.effort, 'request_timeout_seconds': self.timeout,
                'transport': 'fresh CLI print inference with explicit full conversation',
                'temperature': 'not set; provider default', 'user_config_loaded': False,
                'managed_policy': 'Organization-managed policy may still apply.',
                'native_tools': 'Disabled. Proven-unavailable course-tool attempts may self-correct to StructuredOutput; raw attempts remain recorded.'}

    def complete(self, role, prompt, schema_path):
        self.calls[role] += 1
        stem = self.output_dir / f'{role}-{self.calls[role]:03d}'
        schema = json.loads(Path(schema_path).read_text(encoding='utf-8'))
        command = [self.executable, '--print', '--output-format', 'stream-json', '--verbose',
                   '--model', self.model, '--effort', self.effort, '--json-schema', json.dumps(schema),
                   '--tools', '', '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}',
                   '--safe-mode', '--restricted', '--setting-sources', '',
                   '--settings', '{"disableAllHooks":true}', '--disable-slash-commands', '--no-chrome',
                   '--no-session-persistence', '--max-turns', '3',
                   '--system-prompt', 'Return only the requested structured response. Use no native tools except StructuredOutput to format the response. All task information is supplied in the prompt.']
        write_json(stem.with_suffix('.request.json'), {'role': role, 'timestamp': utc_now(),
                   'command': command, 'prompt': prompt, 'schema': schema})
        started = time.monotonic()
        try:
            result = subprocess.run(command, input=prompt, cwd=self.workspace, capture_output=True,
                                    text=True, encoding='utf-8', errors='replace', timeout=self.timeout)
            stdout, stderr = result.stdout, result.stderr
        except subprocess.TimeoutExpired as exc:
            def decode(value): return value.decode('utf-8', errors='replace') if isinstance(value, bytes) else value or ''
            stem.with_suffix('.events.jsonl').write_text(decode(exc.stdout), encoding='utf-8')
            stem.with_suffix('.stderr.txt').write_text(decode(exc.stderr), encoding='utf-8')
            raise ProviderError(f'{role} inference timed out after {self.timeout}s; partial output saved at {stem}') from exc
        stem.with_suffix('.events.jsonl').write_text(stdout, encoding='utf-8')
        stem.with_suffix('.stderr.txt').write_text(stderr, encoding='utf-8')
        if result.returncode:
            if 'authentication_failed' in stdout or 'OAuth session expired' in stdout:
                raise ProviderError("Claude authentication failed. Run 'claude auth login', complete sign-in, then start a new session. Raw failure output was saved.")
            raise ProviderError(f'Claude exited {result.returncode}; inspect {stem.with_suffix(".events.jsonl")} and stderr. Check authentication, model access, and CLI version.')
        value,metadata,models=parse_claude_output(stdout,schema,stem)
        self.resolved_models.update(models)
        write_json(stem.with_suffix('.response.json'), value)
        return value, {**metadata,'role': role, 'request_prefix': stem.name,'duration_seconds':time.monotonic()-started}


PROVIDER_TYPES = (CodexProvider, ClaudeProvider)
