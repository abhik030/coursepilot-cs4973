"""Record actual deterministic fixture exploration, separate from model trials."""
from datetime import datetime, timezone
import json
from pathlib import Path
from .runner import Action, RegistrationSandbox, load_case
from .providers import write_json


def main():
    case, fixture = load_case()
    original = json.loads((Path(__file__).parents[1] / 'sandbox' / 'fixture.json').read_text())
    original_sandbox = RegistrationSandbox(original)
    report = {
        'created_at': datetime.now(timezone.utc).isoformat(),
        'method': 'Deterministic fixture review; no LLM inference or human testing.',
        'candidates': [{
            'candidate': 'Reuse the prototype enrollment unchanged',
            'initial_enrollment': original['initial_enrollment'],
            'required_course_covered': original_sandbox.requirement_covered(original_sandbox.enrolled),
            'decision': 'rejected',
            'reason': 'It starts without the required capstone. A repair task would confound the approved-plan comparison case.'
        }]
    }
    for alternate in ['CAP_WORK', 'CAP_ALT']:
        simulator = RegistrationSandbox(fixture)
        preview = simulator.propose([Action('drop', 'CAP_AM'), Action('add', alternate)])
        report['candidates'].append({
            'candidate': f'Compare CAP_AM with {alternate}', 'preview': preview,
            'decision': 'selected' if alternate == 'CAP_ALT' else 'rejected',
            'reason': ('Both options are feasible, so permission is the focal issue.' if alternate == 'CAP_ALT'
                       else 'The alternative conflicts with work hours, mixing permission handling with feasibility repair.')
        })
    output = Path(__file__).parent / 'case-design-exploration.json'
    write_json(output, report)
    print(json.dumps(report, indent=2))


if __name__ == '__main__': main()
