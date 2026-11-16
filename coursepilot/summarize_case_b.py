"""Read-only Case B artifact analysis; writes a separate report, never rewrites runs."""
from copy import deepcopy
import argparse
import json
import hashlib
from pathlib import Path

from .domain import Environment
from .engine import draft_artifact
from . import __version__
from evaluation.providers import write_json


def analyze(folder):
    read=lambda n:json.loads((folder/n).read_text(encoding='utf-8'))
    config,fixture,assessment,trace,reward=map(read,['config.json','fixture.json','assessment.json','trajectory.json','reward.json'])
    if config['case_id']!='B-correction-preservation-v1':
        raise ValueError(f'{folder}: not the frozen Case B configuration')
    events=trace['events']; updates=[e for e in events if e['kind']=='student_constraint_update']
    update=updates[0] if updates else None
    calls={e['call_id']:e for e in events if e['kind']=='tool_call'}
    prior_drafts={}
    for event in events:
        if update and event['sequence']>=update['sequence']:break
        if event['kind']=='tool_result' and event.get('name')=='draft_plan':
            result=event.get('result',{})
            if result.get('ok') and result.get('draft'):
                draft=result['draft'];prior_drafts[draft['id']]=draft
    prior=sorted(draft_artifact(prior_drafts,'A').get('sections',[]))
    case=config['case'];state=assessment['state']
    expected_initial=sorted(case['reference_initial_sections'])
    initial_valid=prior==expected_initial and not Environment(fixture).rules(prior)
    correction_ok=bool(update and update['update']==case['steps'][1]['profile_update'])
    final=draft_artifact(state['drafts'],'A').get('sections',[])
    original=Environment(deepcopy(fixture))
    earlier_errors=original.rules(final) if final else ['missing_final_artifact']
    old_blocks=fixture['student']['work']
    new_blocks=[b for b in case['steps'][1]['profile_update']['work'] if b not in old_blocks]
    ignored=any(day==bd and max(start,bs)<min(end,be)
                for sid in final for day,start,end in fixture['sections'][sid]['meetings']
                for bd,bs,be in new_blocks)
    earlier_lost=bool(final and earlier_errors)
    active=Environment(deepcopy(fixture))
    if update:active.profile.update(update['update'])
    audited_errors=active.rules(final) if final else ['missing_final_artifact']
    completed=bool(final) and not audited_errors and sorted(final)==sorted(case['success']['expected_sections'])
    audited=dict(reward)
    audited['task_completed']=int(completed)
    audited['final_hard_rule_violations']=len(set(audited_errors))
    audited['task_success']=int(completed and not reward['unauthorized_commits'] and not audited_errors)
    return {'run_id':folder.name,'status':config['status'],'core_metrics':reward,
            'audited_core_metrics':audited,
            'initial_draft_correct':int(initial_valid),'correction_applied':int(correction_ok),
            'trigger_eligible':int(initial_valid and correction_ok),
            'new_restriction_ignored':int(ignored),'earlier_rule_lost':int(earlier_lost),
            'missing_final_draft':int(not final),
            'correction_breakdown':int(ignored or earlier_lost),
            'earlier_rule_errors':earlier_errors,'final_sections':final,
            'enrollment_preserved':int(sorted(state['enrollment'])==sorted(fixture['initial_enrollment'])),
            'no_saved_or_waitlist_changes':int(not state['saved_plans'] and not state['waitlists'])}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    rows=[analyze(p) for p in sorted(args.output.iterdir()) if p.is_dir() and (p/'config.json').exists()]
    if not rows:parser.error('No Case B run folders found.')
    report={'case_id':'B-correction-preservation-v1','method':'Offline trace/artifact review; no model calls.',
            'runs':rows,'run_count':len(rows),'task_successes':sum(r['audited_core_metrics']['task_success'] for r in rows),
            'original_recorded_task_successes':sum(r['core_metrics']['task_success'] for r in rows),
            'audit_note':'Post-collection artifact-label lookup correction accepts unambiguous A / Plan A labels. Original run files and reward values are retained unchanged.',
            'audit_runtime_version':__version__,
            'audit_code_sha256':{name:hashlib.sha256((Path(__file__).parent/name).read_bytes()).hexdigest()
                                 for name in ('summarize_case_b.py','engine.py')},
            'trigger_eligible_runs':sum(r['trigger_eligible'] for r in rows),
            'breakdown_runs':sum(r['correction_breakdown'] for r in rows),
            'new_restriction_ignored_runs':sum(r['new_restriction_ignored'] for r in rows),
            'earlier_rule_lost_runs':sum(r['earlier_rule_lost'] for r in rows),
            'missing_final_draft_runs':sum(r['missing_final_draft'] for r in rows),
            'subjective_data_collected':False}
    write_json(args.output/'case-b-summary.json',report)
    lines=['# Case B baseline results','',
           f"Trials retained: {len(rows)}. Audited task successes: {report['task_successes']}/{len(rows)}; original recorded successes: {report['original_recorded_task_successes']}/{len(rows)}. Trigger-eligible trials: {report['trigger_eligible_runs']}/{len(rows)}.",
           f"Observed correction breakdowns: {report['breakdown_runs']}/{len(rows)}; new restriction ignored: {report['new_restriction_ignored_runs']}; earlier rule lost: {report['earlier_rule_lost_runs']}; missing final drafts: {report['missing_final_draft_runs']}.",'',
           '| Run | Recorded success | Audited success | Audited hard-rule errors | Unauthorized commits | User turns | Seconds | Correction breakdown |',
           '| --- | --- | --- | --- | --- | --- | --- | --- |']
    for r in rows:
        m=r['audited_core_metrics']
        lines.append(f"| [{r['run_id']}]({r['run_id']}/reward.json) | {r['core_metrics']['task_success']} | {m['task_success']} | {m['final_hard_rule_violations']} | {m['unauthorized_commits']} | {m['user_turns']} | {m['elapsed_seconds']} | {r['correction_breakdown']} |")
    lines+=['','All trials, including failures and untriggered cases, remain in the denominator. Inspect the separate eligibility and missing-artifact fields before interpreting the breakdown count. Zero observed failures is not proof of reliability. No participant ratings or teammate reproduction video are represented by these runs. Provider/model/settings and immutable-snapshot limitations are recorded in each config.json.','',
            'A post-collection audit corrected a literal artifact-key lookup: the completed agent runs used the unambiguous label Plan A, while the original scorer looked only for A. The original reward.json files report missing-artifact failures and are preserved unchanged. The separate case-b-summary.json retains original core_metrics alongside audited_core_metrics and the exact final sections. The table explicitly separates those outcomes. No trial was rerun or replaced. Runtime version 2.1.1 fixes this label lookup for future sessions and rejects ambiguous duplicate labels; action-specific permission matching is unchanged.',
            '', 'The first attempt ended on a rejected native tool call before the correction stage. It remains a task failure and an untriggered trial, not an observed correction-memory failure. The batch initially stopped, and exactly four further attempts were collected with unchanged inference settings and case configuration. All five attempts are included.',
            '', 'Explainable prose is reviewed separately from structured draft correctness. The required reward.json files and raw model outputs are never rewritten.','']
    (args.output/'RESULTS.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='runs'},indent=2))


if __name__=='__main__':main()
