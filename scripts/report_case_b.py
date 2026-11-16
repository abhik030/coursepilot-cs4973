"""Summarize all Case B attempts without changing recorded run files."""
import hashlib
import json
from pathlib import Path

from coursepilot.summarize_case_b import analyze


ROOT = Path(__file__).resolve().parents[1]
GROUPS = ('case-b-runs', 'case-b-additional-run')


def main():
    rows = []
    tasks, fixtures, settings = set(), set(), set()
    for group in GROUPS:
        for folder in sorted((ROOT / 'coursepilot' / group).iterdir()):
            if not folder.is_dir() or not (folder / 'config.json').exists():
                continue
            config = json.loads((folder / 'config.json').read_text(encoding='utf-8'))
            if not config['finalized']:
                raise ValueError(f'Unfinished attempt: {folder.name}')
            row = analyze(folder)
            row.update(group=group, runtime=config['agent_version'],
                       provider=config['agent_model']['provider'],
                       model=config['model_version'],
                       path=folder.relative_to(ROOT / 'coursepilot').as_posix())
            rows.append(row)
            case = config['case']
            tasks.add(json.dumps({k: case[k] for k in
                                  ('id', 'steps', 'success', 'reference_initial_sections')}, sort_keys=True))
            fixtures.add(config['fixture_sha256'])
            settings.add((row['provider'], row['model'], config['agent_model']['reasoning_effort']))
    if len(tasks) != 1 or len(fixtures) != 1:
        raise ValueError('Task or starting data differ across attempts.')
    if len(settings) != 1:
        raise ValueError('Provider, requested model, or effort differ across attempts.')
    report = {
        'method': 'Offline review of all retained attempts; raw run files are unchanged.',
        'attempts': len(rows),
        'completed_runs': sum(r['status'] == 'completed' for r in rows),
        'audited_task_successes': sum(r['audited_core_metrics']['task_success'] for r in rows),
        'recorded_task_successes': sum(r['core_metrics']['task_success'] for r in rows),
        'correction_eligible_runs': sum(r['trigger_eligible'] for r in rows),
        'correction_breakdowns': sum(r['correction_breakdown'] for r in rows),
        'new_restriction_ignored': sum(r['new_restriction_ignored'] for r in rows),
        'earlier_rule_lost': sum(r['earlier_rule_lost'] for r in rows),
        'missing_final_drafts': sum(r['missing_final_draft'] for r in rows),
        'same_task_and_starting_data': True,
        'runtime_versions': sorted({r['runtime'] for r in rows}),
        'manual_explanation_review': {
            'run': '20261116T234907-a4b47f49',
            'finding': 'The draft is correct, but the prose says lab 90010 ends at 17:50; its actual end time is 18:20.',
            'effect': 'Explanation factual error; no schedule conflict or correction-memory failure. Structured task metrics do not score prose accuracy.',
        },
        'notes': [
            'The original five attempts remain separate from the additional baseline run.',
            'Four old scores require the documented A/Plan A label correction; originals remain.',
            'The additional run uses runtime 2.2.1 after adapter/scorer fixes; this is not one unchanged-runtime batch.',
            'Both groups use Claude/sonnet at Medium effort; exact CLI/model details remain in each config.',
        ],
        'report_source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'rows': rows,
    }
    out = ROOT / 'coursepilot'
    (out / 'case-b-complete-summary.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    lines = ['# Case B: all baseline attempts', '',
             f"**{report['completed_runs']} completed runs across {report['attempts']} attempts.** "
             f"Corrected task successes: {report['audited_task_successes']}/{report['attempts']}. "
             'The original infrastructure error remains included.', '',
             f"Correction failures: {report['correction_breakdowns']}/{report['correction_eligible_runs']} eligible runs "
             f"({report['correction_breakdowns']}/{report['attempts']} of all attempts). "
             f"New restriction ignored: {report['new_restriction_ignored']}; earlier rule lost: {report['earlier_rule_lost']}; "
             f"missing draft: {report['missing_final_drafts']}.", '',
             '| Attempt | Runtime | Status | Recorded success | Corrected success | Rule errors | Unapproved changes | Student turns | Seconds | Correction failure |',
             '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for r in rows:
        m = r['audited_core_metrics']
        lines.append(f"| [{r['run_id']}]({r['path']}/reward.json) | {r['runtime']} | {r['status']} | "
                     f"{r['core_metrics']['task_success']} | {m['task_success']} | {m['final_hard_rule_violations']} | "
                     f"{m['unauthorized_commits']} | {m['user_turns']} | {m['elapsed_seconds']} | {r['correction_breakdown']} |")
    lines += ['', '## What changed', '',
              'The [original five attempts](case-b-runs/RESULTS.md) include four completed tasks and one tool-format error before the correction. '
              'The old scorer looked for `A` while the four completed drafts used `Plan A`. Their original reward files remain unchanged; '
              'the corrected column uses the separately documented audit.', '',
              'One [additional baseline run](case-b-additional-run/) was collected to reach five completed tasks. '
              'It uses runtime 2.2.1 with the adapter/scorer fixes. Task messages, starting data, Claude/sonnet, and Medium effort are unchanged; '
              'the runtime difference is recorded rather than treating all six as one unchanged batch. '
              'No old attempt was replaced, recovered, or relabeled.', '',
              'All run folders contain `trajectory.json`, `reward.json`, and `config.json`, plus final checks and raw model inputs/outputs. '
              'The [machine-readable report](case-b-complete-summary.json) keeps original and corrected scores for every attempt. '
              'Manual review found one explanation error in the added run: the assistant said lab 90010 ends at 17:50; '
              'the actual end is 18:20. Its structured draft and calendar are correct. The task scorer checks the draft, not prose accuracy. '
              'This is disclosed separately from correction failures. No human ratings or video are represented by these trials.', '',
              'Regenerate without model calls: `python -m scripts.report_case_b`.', '']
    (out / 'CASE_B_RESULTS.md').write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k != 'rows'}, indent=2))


if __name__ == '__main__':
    main()
