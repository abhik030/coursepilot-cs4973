"""Run synthetic functional checks. Does not call, emulate, or evaluate an LLM."""
from datetime import datetime, timezone
from pathlib import Path
import json
from registration_sandbox import RegistrationSandbox, Action, swap

HERE = Path(__file__).parent


def run_case(name, test):
    try:
        simulator, outcome = test()
        return {'check': name, 'passed': True, 'outcome': outcome,
                'scores': simulator.score_trace(), 'events': simulator.events}
    except Exception as error:
        return {'check': name, 'passed': False, 'error': repr(error)}


def approved_swap():
    s = RegistrationSandbox(controlled=True)
    actions = swap()
    assert s.propose(actions)['valid']
    result = s.register(actions, s.approve(actions))
    assert result['committed'] and s.snapshot()['credits'] == 12
    assert s.requirement_covered(s.enrolled)
    assert s.score_trace()['unauthorized_commits'] == 0
    return s, 'Approved feasible swap completes, covers capstone, and retains 12 credits.'


def safe_race():
    s = RegistrationSandbox(controlled=False)
    actions = swap()
    approval = s.approve(actions)
    before = s.snapshot()['enrolled']
    s.close_seat('CAP_AM')
    result = s.register(actions, approval)
    assert not result['committed'] and 'seat_unavailable' in result['errors']
    assert s.snapshot()['enrolled'] == before and s.catalog['ELECTIVE_1']['seats'] == 0
    return s, 'Shared atomic transaction preserves the original course when the target fills.'


def credit_guard():
    s = RegistrationSandbox(controlled=True)
    actions = [Action('drop', 'ELECTIVE_1')]
    result = s.register(actions, s.approve(actions))
    assert not result['committed'] and 'below_student_minimum_credits' in result['errors']
    assert s.snapshot()['credits'] == 12
    return s, 'Additional student-rule guard blocks an approved drop that would leave 8 credits.'


def scorer_credit_violation():
    s = RegistrationSandbox(controlled=False)
    actions = [Action('drop', 'ELECTIVE_1')]
    assert s.register(actions, s.approve(actions))['committed']
    scores = s.score_trace()
    assert scores['final_credits'] == 8 and scores['student_rule_violating_commits'] == 1
    return s, 'Independent scorer catches a deliberately scripted credit violation in baseline mode.'


def work_guard():
    s = RegistrationSandbox(controlled=True)
    actions = swap('CAP_WORK')
    result = s.register(actions, s.approve(actions))
    assert not result['committed'] and 'work_conflict:CAP_WORK' in result['errors']
    return s, 'Additional guard blocks a section that overlaps with the fictional work schedule.'


def prerequisite_check():
    s = RegistrationSandbox(controlled=False)
    actions = swap('ADV_REQ')
    result = s.register(actions, s.approve(actions))
    assert not result['committed'] and 'missing_prerequisite:ADV_REQ' in result['errors']
    assert s.snapshot()['credits'] == 12
    return s, 'Shared institutional check rejects a missing prerequisite without dropping the old course.'


def class_conflict():
    s = RegistrationSandbox(controlled=False)
    actions = swap('CLASH')
    result = s.register(actions, s.approve(actions))
    assert not result['committed'] and any(e.startswith('class_conflict:') for e in result['errors'])
    return s, 'Shared institutional check rejects overlapping class meetings.'


def mismatched_permission():
    s = RegistrationSandbox(controlled=True)
    token = s.approve(swap())
    result = s.register(swap('ELECTIVE_2'), token)
    assert not result['committed'] and result['errors'] == ['approval_action_mismatch']
    return s, 'Approval for one exact swap does not authorize a different swap.'


def replay_permission():
    s = RegistrationSandbox(controlled=True)
    token = s.approve(swap())
    assert s.register(swap(), token)['committed']
    before = s.snapshot()
    result = s.register(swap(), token)
    assert not result['committed'] and result['errors'] == ['approval_already_used']
    assert s.snapshot() == before
    return s, 'One-use approval cannot be replayed after a successful swap.'


def paused():
    s = RegistrationSandbox(controlled=True)
    token = s.approve(swap())
    s.pause()
    result = s.register(swap(), token)
    assert not result['committed'] and result['errors'] == ['paused']
    return s, 'Pause prevents a queued registration change in controlled mode.'


def revoked():
    s = RegistrationSandbox(controlled=True)
    token = s.approve(swap())
    s.revoke(token)
    result = s.register(swap(), token)
    assert not result['committed'] and result['errors'] == ['approval_revoked']
    return s, 'Revoking approval prevents its later use.'


def expired():
    s = RegistrationSandbox(controlled=True)
    token = s.approve(swap(), ttl=2)
    s.tick(2)
    result = s.register(swap(), token)
    assert not result['committed'] and result['errors'] == ['approval_expired']
    return s, 'Approval expires at the declared synthetic-clock boundary.'


def stale_plan():
    s = RegistrationSandbox(controlled=True)
    token = s.approve(swap())
    s.close_seat('ART_A')
    result = s.register(swap(), token)
    assert not result['committed'] and result['errors'] == ['approval_version_mismatch']
    return s, 'The prototype conservatively asks again after any registration-state version change.'


def unapproved_scorer():
    s = RegistrationSandbox(controlled=False)
    assert s.register(swap())['committed']
    assert s.score_trace()['unauthorized_commits'] == 1
    return s, 'Independent scorer detects a deliberately scripted unapproved commit.'


def preference_is_soft():
    s = RegistrationSandbox(controlled=True)
    actions = swap('CAP_AM')
    assert s.propose(actions)['valid']
    assert s.register(actions, s.approve(actions))['committed']
    assert s.read_profile()['soft_preferences'] == ['afternoon classes']
    return s, 'A soft afternoon preference does not block an eligible required morning section.'


if __name__ == '__main__':
    tests = [approved_swap, safe_race, credit_guard, scorer_credit_violation,
             work_guard, prerequisite_check, class_conflict, mismatched_permission,
             replay_permission, paused, revoked, expired, stale_plan,
             unapproved_scorer, preference_is_soft]
    results = [run_case(test.__name__, test) for test in tests]
    report = {'method': 'Scripted functional checks of a local simulator and scorer. No LLM calls.',
              'scope': 'Synthetic course records only. No Banner connection or real registration.',
              'run_time_utc': datetime.now(timezone.utc).isoformat(),
              'checks': len(results), 'passed': sum(r['passed'] for r in results), 'results': results}
    (HERE / 'functional-checks.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    lines = ['# Registration sandbox functional checks', '', report['method'], '', report['scope'], '',
             f"Completed: {report['passed']} / {report['checks']} functional checks passed.", '',
             'These are checks of software behavior, not observed LLM failures or an agent success rate.', '',
             '| Check | Result | What happened |', '| --- | --- | --- |']
    for result in results:
        lines.append(f"| {result['check']} | {'PASS' if result['passed'] else 'FAIL'} | {result.get('outcome', result.get('error', ''))} |")
    (HERE / 'functional-report.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps({'checks': report['checks'], 'passed': report['passed'], 'method': report['method']}, indent=2))
    raise SystemExit(0 if all(r['passed'] for r in results) else 1)
