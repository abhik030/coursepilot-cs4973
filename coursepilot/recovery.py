"""Resume an unfinished Case B draft from a saved, corrected CLI response. No inference."""
from copy import deepcopy
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import threading
import time

from . import __version__
from .domain import Environment
from .engine import Session,HERE
from .providers import ClaudeProvider,parse_claude_output
from evaluation.providers import write_json


def recover_saved_draft(folder):
    folder=Path(folder)
    read=lambda name:json.loads((folder/name).read_text(encoding='utf-8'))
    config,assessment,trace,reward,fixture=map(read,['config.json','assessment.json','trajectory.json','reward.json','fixture.json'])
    if config.get('finalized') or config.get('mode')!='human' or config.get('status')!='error' or config.get('case_id')!='B-correction-preservation-v1':
        raise ValueError('Only an unfinished, stopped human Case B run can recover a saved draft.')
    if folder.name!=config['run_id']:raise ValueError('Run identity mismatch.')
    requests=sorted((folder/'provider').glob('agent-*.request.json'))
    if not requests:raise ValueError('No saved agent request exists.')
    request_file=requests[-1];stem=request_file.with_suffix('').with_suffix('')
    request=json.loads(request_file.read_text(encoding='utf-8'))
    raw=stem.with_suffix('.events.jsonl').read_text(encoding='utf-8')
    value,metadata,models=parse_claude_output(raw,request['schema'],stem)
    Session.validate_decision(value)
    if value['kind']!='tool' or value['tool']!='draft_plan':
        raise ValueError('Saved-response recovery only applies a draft revision, not a persistent action.')
    if not metadata['unavailable_course_tool_attempts']:
        raise ValueError('This response does not match the corrected formatting issue.')
    state=assessment['state']
    if state['paused']:raise ValueError('This run was paused; no draft was applied.')
    s=Session.__new__(Session)
    s.id,s.output,s.lock=config['run_id'],folder,threading.RLock()
    s.case,s.fixture,s.steps=config['case'],fixture,config['user_stages']
    s.code_hashes=config['code_sha256']
    s.env=Environment(fixture,controlled=config['agent']=='controlled')
    s.env.catalog=deepcopy(state['catalog']);s.env.profile=deepcopy(state['student'])
    for attribute,key in [('drafts','drafts'),('saved','saved_plans'),('pending','pending_registration'),
                          ('enrolled','enrollment'),('enrollment_version','enrollment_version'),
                          ('waitlists','waitlists'),('permissions','permissions'),('paused','paused')]:
        setattr(s.env,attribute,deepcopy(state[key]))
    s.events=deepcopy(trace['events'])
    s.env.audit=[deepcopy(e['event']) for e in s.events if e['kind']=='state_action']
    s.history=json.loads(request['prompt'])['conversation']
    s.chat=[{'role':'user' if e['actor']=='user' else 'assistant','message':e['message'],
             'reports':e.get('reports',[]),'timestamp':e['timestamp']}
            for e in s.events if e['kind']=='message' and e['actor'] in ('user','agent')]
    s.reports=assessment['reports'];s.protocol_issues=assessment['protocol_issues']
    s.agent,s.mode=config['agent'],config['mode']
    s.stage=max(e.get('stage',0) for e in s.events if e['kind']=='message' and e['actor']=='user')
    s.applied_stage_updates={i for i,step in enumerate(s.steps) if any(e['kind']=='student_constraint_update' and e['update']==step.get('profile_update') for e in s.events)}
    s.user_turns=reward['user_turns'];s.agent_steps=reward['agent_steps']+1
    s.model_calls=reward['model_calls']+1
    s.input_tokens=reward['input_tokens']+metadata['usage']['input_tokens']
    s.output_tokens=reward['output_tokens']+metadata['usage']['output_tokens']
    first=next(e['timestamp'] for e in s.events if e['kind']=='message' and e['actor']=='user')
    s.started=time.monotonic()-(datetime.now(timezone.utc)-datetime.fromisoformat(first)).total_seconds()
    s.finished=None;s.frozen=False;s.busy=False;s.worker=None;s.epoch=s.user_turns+1;s.initial_a_signature=None
    s.status,s.error='awaiting_student',None
    p=ClaudeProvider.__new__(ClaudeProvider)
    p.output_dir=folder/'provider';p.workspace=p.output_dir/'model-workspace';p.executable=shutil.which('claude')
    p.model=config['model_version'];p.effort=config['agent_model']['reasoning_effort'];p.timeout=120
    p.version=config['agent_model']['cli_version'];p.resolved_models=set(config['agent_model'].get('resolved_models',[]))|models
    p.calls={role:max((int(re.search(r'-(\d+)\.request',f.name)[1]) for f in p.output_dir.glob(role+'-*.request.json')),default=0) for role in ('agent','user')}
    s.provider=p
    result=s.env.tool('draft_plan',value['target'],value['sections'])
    if not result.get('ok'):raise ValueError('Saved draft could not be applied: '+str(result.get('errors')))
    backup=folder/'before-recovery'
    backup.mkdir(exist_ok=False)
    for name in ('config.json','reward.json','assessment.json','trajectory.json','trajectory.jsonl'):
        shutil.copyfile(folder/name,backup/name)
    s.continuation={'type':'saved_response_recovery','original_error':config['error'],
                    'original_agent_version':config['agent_version'],'recovery_version':__version__,
                    'request_prefix':stem.name,'new_model_inference':False,
                    'source_sha256':{name:hashlib.sha256((HERE/name).read_bytes()).hexdigest() for name in ('providers.py','engine.py','recovery.py')},
                    'note':'Recovered the saved, corrected model response without another model call. The draft revision is applied; review it, then Finish & save. The original error and pre-recovery files are retained.'}
    s.record('saved_response_recovery','application',**s.continuation)
    final=next(e for e in metadata['events'] if e.get('type')=='result')
    metadata.update({'role':'agent','request_prefix':stem.name,'duration_seconds':final.get('duration_ms',0)/1000,
                     'recovered_saved_response':True,'new_model_inference':False})
    write_json(stem.with_suffix('.response.json'),value)
    s.record('model_response','agent',response=value,provider=metadata)
    s.history.append({'role':'agent','decision':value})
    event=s.record('message','agent',message=value['message'],reports=value['reports'])
    s.chat.append({'role':'assistant','message':value['message'],'reports':value['reports'],'timestamp':event['timestamp']})
    call_id='recovered-tool-'+str(s.agent_steps)
    s.record('tool_call','agent',call_id=call_id,name='draft_plan',arguments={'target':value['target'],'sections':value['sections']})
    s.record('tool_result','environment',call_id=call_id,name='draft_plan',result=result)
    s.history.append({'role':'tool','name':'draft_plan','result':result})
    s.persist()
    return s
