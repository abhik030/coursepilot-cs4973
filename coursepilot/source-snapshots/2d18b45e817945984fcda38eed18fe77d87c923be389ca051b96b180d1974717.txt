"""Run real simulated-student sessions; uses the same Session as the browser."""
import argparse
import json
from pathlib import Path
from .engine import HERE, Session
from evaluation.providers import write_json


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--runs',type=int,default=1)
    parser.add_argument('--agent',choices=['baseline','controlled'],default='baseline')
    parser.add_argument('--model',default='gpt-6.1-sol')
    parser.add_argument('--effort',choices=['low','medium','high'],default='medium')
    parser.add_argument('--output',type=Path,default=HERE/'runs')
    parser.add_argument('--case',type=Path)
    args=parser.parse_args()
    if not 1<=args.runs<=20: parser.error('Choose 1–20 runs.')
    rows=[]
    for index in range(args.runs):
        session=Session(args.output,args.agent,'simulated',args.model,args.effort,case_path=args.case)
        print(f'Run {index+1}/{args.runs}: {session.id}',flush=True)
        session.simulate()
        row={'id':session.id,'status':session.status,'metrics':session.metrics()}
        rows.append(row)
        print(json.dumps(row),flush=True)
        if session.error: break
    result={'case_id':session.case['id'],'agent':args.agent,'runs':rows,
            'completed':sum(r['status']=='completed' for r in rows),
            'task_successes':sum(r['metrics']['task_success'] for r in rows),
            'approval_breakdowns':sum(r['metrics']['approval_breakdown'] for r in rows),
            'subjective_data_collected':False}
    write_json(args.output/f'summary-{args.agent}.json',result)
    return 0 if len(rows)==args.runs and all(r['status']=='completed' for r in rows) else 1


if __name__=='__main__':raise SystemExit(main())
