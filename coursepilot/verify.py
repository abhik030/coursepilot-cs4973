"""Offline provenance and permission checks on completed v2 runs. No inference."""
import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
from .domain import signature
from .engine import HERE
from evaluation.providers import write_json


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=HERE/'runs')
    args=parser.parse_args()
    rows=[]
    for folder in sorted(args.output.iterdir()):
        if not folder.is_dir() or not (folder/'config.json').exists():continue
        read=lambda name:json.loads((folder/name).read_text(encoding='utf-8'))
        config,reward,trace,fixture=map(read,['config.json','reward.json','trajectory.json','fixture.json'])
        if not config['finalized']:continue
        events=trace['events'];issues=[];archived_sources=[]
        def check(test,detail):
            if not test:issues.append(detail)
        check([e['sequence'] for e in events]==list(range(len(events))),'Event ordering')
        stamps=[datetime.fromisoformat(e['timestamp']) for e in events]
        check(stamps==sorted(stamps),'Timestamp ordering')
        check(all(type(value) in (int,float) for value in reward.values()),'Numeric metrics')
        check(signature(fixture)==config['fixture_sha256'],'Fixture hash')
        for name,expected in config['code_sha256'].items():
            matches=hashlib.sha256((HERE/name).read_bytes()).hexdigest()==expected
            if not matches:
                archive=HERE/'source-snapshots'/(expected+'.txt')
                matches=archive.exists() and hashlib.sha256(archive.read_bytes()).hexdigest()==expected
                if matches:archived_sources.append(name)
            check(matches,'Source hash: '+name)
        calls={e['call_id']:e for e in events if e['kind']=='tool_call'}
        results={e['call_id']:e for e in events if e['kind']=='tool_result'}
        check(set(calls)==set(results),'Paired course tools')
        check(all(calls[k]['sequence']<results[k]['sequence'] for k in calls),'Tool result ordering')
        receipts={e['receipt']['id']:e for e in events if e['kind']=='approval'}
        actions=[e for e in events if e['kind']=='state_action']
        used=set();unauthorized=0
        for entry in actions:
            action=entry['event'];pid=action['permission_id'];applicable=False
            if pid in receipts:
                receipt_event=receipts[pid];receipt=receipt_event['receipt'];message=events[receipt['message_id']]
                applicable=(receipt_event['sequence']<entry['sequence'] and pid not in used
                            and receipt['signature']==signature(action['action']) and message['actor']=='user'
                            and message.get('intent') in ('save','register','join_waitlist'))
                check(applicable==action['authorized'],'Permission truth mismatch')
            if action['committed']:
                unauthorized+=not applicable
                if applicable:used.add(pid)
        check(unauthorized==reward['unauthorized_commits'],'Unauthorized commit metric')
        check(len([e for e in events if e['kind']=='message' and e['actor']=='user'])==reward['user_turns'],'Student turns')
        responses=[e for e in events if e['kind']=='model_response']
        check(len(responses)==reward['model_calls'],'Model-call count')
        for response in responses:
            prefix=folder/'provider'/response['provider']['request_prefix']
            if not prefix.with_suffix('.response.json').exists():
                check(config['evidence_kind']!='llm_evaluation','Missing raw response');continue
            check(json.loads(prefix.with_suffix('.response.json').read_text(encoding='utf-8'))==response['response'],'Raw response differs')
            raw=[json.loads(line) for line in prefix.with_suffix('.events.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
            check(raw==response['provider']['events'],'Raw provider event completeness')
        rows.append({'id':folder.name,'passed':not issues,'issues':issues,'status':config['status'],
                     'student_turns':reward['user_turns'],'tool_pairs':len(calls),'archived_sources':archived_sources})
    report={'method':'Offline trace and source verification, no model calls.','checked':len(rows),
            'passed':sum(r['passed'] for r in rows),'runs':rows}
    write_json(args.output/'verification.json',report)
    print(json.dumps(report,indent=2))
    return 0 if rows and all(r['passed'] for r in rows) else 1


if __name__=='__main__':raise SystemExit(main())
