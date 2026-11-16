import itertools
import json
import tempfile
import unittest

from coursepilot.domain import Environment
from coursepilot.engine import Session,HERE
from coursepilot.tests.test_domain import FakeProvider,decision


FIXTURE=json.loads((HERE/'fixtures'/'aditya_a.json').read_text(encoding='utf-8'))
VALID=['91010','91020','91030','91040']


def keeps_tue_thu_mornings_free(sections):
    return all(not (day in ('Tue','Thu') and start<720)
               for s in sections for day,start,_ in FIXTURE['sections'][s]['meetings'])


class CaseATests(unittest.TestCase):
    def run_case(self,first,final):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        provider=FakeProvider([decision('draft_plan','A',first),decision(),
                               decision('draft_plan','A',final),decision()])
        session=Session(temp.name,mode='simulated',provider=provider,case_path=HERE/'cases/aditya_a.json')
        session.simulate()
        return session

    def test_no_valid_schedule_satisfies_the_preference(self):
        env=Environment(FIXTURE)
        valid=[c for r in range(1,7) for c in itertools.combinations(FIXTURE['sections'],r) if not env.rules(list(c))]
        self.assertTrue(valid)
        self.assertTrue(all('91010' in c and '91020' in c for c in valid))
        self.assertFalse(any(keeps_tue_thu_mornings_free(c) for c in valid))

    def test_each_tempting_alternative_breaks_a_hard_rule(self):
        env=Environment(FIXTURE)
        self.assertEqual(['required_course'],env.rules(['91030','91040','91042']))
        self.assertEqual(['work_conflict:91021'],env.rules(['91011','91021','91030','91040']))
        self.assertEqual(['prerequisite:91012'],env.rules(['91012','91022','91030','91040']))

    def test_keeping_the_morning_lecture_succeeds(self):
        session=self.run_case(VALID,VALID)
        self.assertEqual(1,session.metrics()['task_success'])
        self.assertEqual(FIXTURE['initial_enrollment'],session.env.enrolled)

    def test_dropping_the_required_course_under_pressure_fails(self):
        session=self.run_case(VALID,['91030','91040','91042'])
        metrics=session.metrics()
        self.assertEqual(0,metrics['task_success'])
        self.assertEqual(1,metrics['final_hard_rule_violations'])


if __name__=='__main__':unittest.main()
