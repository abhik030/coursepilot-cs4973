"""Validate the recorded batch's provenance and trace/file completeness without inference."""
import argparse
import hashlib
import json
import math
from pathlib import Path
from datetime import datetime
from .providers import write_json
from .runner import PROJECT, fingerprint


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=Path(__file__).parent / 'runs')
    args = parser.parse_args()
    folders = sorted(p for p in args.output.iterdir() if p.is_dir() and (p / 'config.json').exists())
    results = []
    for folder in folders:
        checks = []
        def check(condition, message):
            if not condition: checks.append(message)
        config, reward, trace, fixture, assessment = [read(folder / name) for name in
            ['config.json', 'reward.json', 'trajectory.json', 'fixture.json', 'assessment.json']]
        events = trace['events']
        check(config['evidence_kind'] == 'llm_evaluation', 'not real LLM evidence')
        check(config['status'] == 'completed', 'run did not complete')
        check(config['fixture_sha256'] == fingerprint(fixture), 'fixture hash mismatch')
        check(config['case_sha256'] == fingerprint(config['case']), 'case hash mismatch')
        for name, expected in config['code_sha256'].items():
            check(hashlib.sha256((PROJECT / name).read_bytes()).hexdigest() == expected,
                  'current source differs from recorded code: ' + name)
        check([e['sequence'] for e in events] == list(range(len(events))), 'out-of-order sequence')
        stamps = [datetime.fromisoformat(e['timestamp']) for e in events]
        check(stamps == sorted(stamps), 'timestamps not monotonic')
        check(all(type(v) in (int, float) and math.isfinite(v) for v in reward.values()), 'non-numeric/non-finite metric')
        calls, responses = {}, {}
        for event in events:
            if event['kind'] == 'tool_call': calls[event['call_id']] = event
            if event['kind'] == 'tool_result': responses[event['call_id']] = event
        check(set(calls) == set(responses), 'unpaired tool call/result')
        for name in calls:
            check(calls[name]['sequence'] < responses[name]['sequence'], 'tool result precedes call')
        model_requests = [e for e in events if e['kind'] == 'model_request']
        model_responses = [e for e in events if e['kind'] == 'model_response']
        check(len(model_requests) == len(model_responses) == reward['model_calls'], 'model request/response count mismatch')
        for request, response in zip(model_requests, model_responses):
            prefix = folder / 'provider' / response['provider']['request_prefix']
            saved_request = read(prefix.with_suffix('.request.json'))
            saved_response = read(prefix.with_suffix('.response.json'))
            raw_events = [json.loads(line) for line in prefix.with_suffix('.events.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
            check(request['prompt'] == saved_request['prompt'], 'prompt differs from raw request')
            check(response['response'] == saved_response, 'response differs from raw response')
            check(response['provider']['events'] == raw_events, 'raw provider events incomplete')
            check(all(e.get('item', {}).get('type') in (None, 'agent_message', 'reasoning') for e in raw_events),
                  'unexpected native tool/error item')
        student_messages = [e for e in events if e['kind'] == 'message' and e['actor'] == 'user']
        check(len(student_messages) == reward['user_turns'], 'user-turn count mismatch')
        check(student_messages[0]['message'] == config['case']['initial_prompt'], 'fixed prompt changed')
        check(assessment['final_state']['enrolled'] == sorted(fixture['initial_enrollment']), 'saved plan changed')
        results.append({'run_id': folder.name, 'passed': not checks, 'issues': checks,
                        'tool_pairs': len(calls), 'model_calls': len(model_responses)})
    result = {'method': 'Offline integrity verification; no model inference or subjective scoring.',
              'run_count': len(results), 'passed': sum(r['passed'] for r in results), 'results': results}
    write_json(args.output / 'verification.json', result)
    print(json.dumps(result, indent=2))
    return 0 if results and all(r['passed'] for r in results) else 1


if __name__ == '__main__': raise SystemExit(main())
