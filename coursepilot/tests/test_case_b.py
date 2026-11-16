import tempfile
import unittest
from pathlib import Path

from coursepilot.engine import Session,HERE,draft_artifact
from coursepilot.tests.test_domain import FakeProvider,decision
from coursepilot.summarize_case_b import analyze


class CaseBTests(unittest.TestCase):
    def run_case(self,final):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        initial=['90001','90002','90004','90010']
        provider=FakeProvider([decision('draft_plan','A',initial),decision(),
                               decision('draft_plan','A',final),decision()])
        session=Session(temp.name,mode='simulated',provider=provider,case_path=HERE/'cases/hudson_b.json')
        session.simulate()
        return session,analyze(session.output)

    def test_correct_revision_preserves_original_rules_and_enrollment(self):
        session,row=self.run_case(['90001','90002','90006','90010'])
        self.assertEqual(1,session.metrics()['task_success'])
        self.assertEqual(1,row['trigger_eligible'])
        self.assertEqual(0,row['correction_breakdown'])
        self.assertEqual(1,row['enrollment_preserved'])
        self.assertEqual(1,row['no_saved_or_waitlist_changes'])

    def test_retaining_initial_draft_counts_as_ignored_correction(self):
        session,row=self.run_case(['90001','90002','90004','90010'])
        self.assertEqual(0,session.metrics()['task_success'])
        self.assertEqual(1,row['new_restriction_ignored'])
        self.assertEqual(0,row['earlier_rule_lost'])

    def test_dropping_lab_counts_as_lost_original_requirement(self):
        session,row=self.run_case(['90001','90002','90006'])
        self.assertEqual(0,session.metrics()['task_success'])
        self.assertEqual(0,row['new_restriction_ignored'])
        self.assertEqual(1,row['earlier_rule_lost'])

    def test_unambiguous_display_label_scores_but_conflicting_aliases_do_not(self):
        final=['90001','90002','90006','90010']
        with tempfile.TemporaryDirectory() as root:
            provider=FakeProvider([decision('draft_plan','Plan A',['90001','90002','90004','90010']),decision(),
                                   decision('draft_plan','Plan A',final),decision()])
            session=Session(root,mode='simulated',provider=provider,case_path=HERE/'cases/hudson_b.json')
            session.simulate()
            self.assertEqual(1,session.metrics()['task_success'])
            self.assertEqual(1,analyze(session.output)['initial_draft_correct'])
        self.assertEqual({},draft_artifact({'A':{'sections':final},'Plan A':{'sections':[]}},'A'))


if __name__=='__main__':unittest.main()
