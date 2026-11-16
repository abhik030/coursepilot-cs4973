from __future__ import annotations
from copy import deepcopy
import hashlib
import json


def signature(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


GRADES = {grade: i for i, grade in enumerate(['F', 'D-', 'D', 'D+', 'C-', 'C', 'C+', 'B-', 'B', 'B+', 'A-', 'A'])}


class Environment:
    """Fictional registration. Institutional checks are shared in both conditions."""
    def __init__(self, fixture, controlled=False):
        self.fixture = deepcopy(fixture)
        self.catalog = self.fixture['sections']
        self.profile = self.fixture['student']
        self.controlled = controlled
        self.enrolled = sorted(self.fixture['initial_enrollment'])
        self.initial_enrollment = list(self.enrolled)
        self.enrollment_version = 1
        self.drafts, self.saved, self.pending, self.waitlists = {}, {}, None, {}
        self.permissions, self.audit = [], []
        self.paused = False

    def credits(self, sections):
        return sum(self.catalog[s]['credits'] for s in sections)

    def rules(self, sections, include_student=True):
        sections = sorted(sections)
        if len(set(sections)) != len(sections): return ['duplicate_section']
        if any(s not in self.catalog for s in sections): return ['unknown_section']
        problems = []
        courses = [self.catalog[s]['course'] for s in sections]
        if len(set(courses)) != len(courses): problems.append('duplicate_course')
        if self.credits(sections) > self.profile['max_credits']: problems.append('maximum_credits')
        for index, sid in enumerate(sections):
            section = self.catalog[sid]
            for group in section.get('prerequisite_groups', []):
                if not any(GRADES.get(self.profile['completed'].get(r['course'], 'F'), -1) >= GRADES[r['minimum_grade']] for r in group):
                    problems.append('prerequisite:' + sid)
            if not set(section.get('requires_sections', [])) <= set(sections): problems.append('corequisite:' + sid)
            for other in sections[index+1:]:
                if any(a[0] == b[0] and max(a[1], b[1]) < min(a[2], b[2])
                       for a in section['meetings'] for b in self.catalog[other]['meetings']):
                    problems.append('class_conflict:' + sid + ':' + other)
            if include_student and any(a[0] == b[0] and max(a[1], b[1]) < min(a[2], b[2])
                    for a in section['meetings'] for b in self.profile['work']): problems.append('work_conflict:' + sid)
        if include_student:
            if self.credits(sections) < self.profile['min_credits']: problems.append('minimum_credits')
            if not set(self.profile['required_courses']) <= set(courses): problems.append('required_course')
            if not set(self.profile['protected_sections']) <= set(sections): problems.append('protected_course')
        return sorted(set(problems))

    def snapshot(self):
        return deepcopy({'term': self.fixture['term'], 'student': self.profile, 'catalog': self.catalog,
            'drafts': self.drafts, 'saved_plans': self.saved, 'pending_registration': self.pending,
            'enrollment': self.enrolled, 'enrollment_version': self.enrollment_version,
            'registered_credits': self.credits(self.enrolled), 'waitlists': self.waitlists,
            'permissions': self.permissions, 'paused': self.paused,
            'registration_open': self.fixture['registration_open']})

    def payload(self, kind, target):
        if kind == 'save_plan':
            plan = self.drafts.get(target)
            if not plan: raise ValueError('Draft plan does not exist')
            return {'kind': kind, 'target': target, 'draft_version': plan['version'],
                    'saved_version': self.saved.get(target, {}).get('version', 0), 'sections': sorted(plan['sections'])}
        if kind == 'register_plan':
            plan = self.saved.get(target)
            if not plan: raise ValueError('Saved plan does not exist')
            return {'kind': kind, 'target': target, 'saved_version': plan['version'],
                    'sections': sorted(plan['sections']), 'enrollment_version': self.enrollment_version}
        if kind in ('join_waitlist', 'accept_offer'):
            if target not in self.catalog: raise ValueError('Unknown section')
            return {'kind': kind, 'target': target, 'enrollment_version': self.enrollment_version}
        raise ValueError('Unknown approval action')

    def authorize(self, kind, target, message_id):
        payload = self.payload(kind, target)
        receipt = {'id': f'permission-{len(self.permissions)+1}', 'message_id': message_id,
                   'action': payload, 'signature': signature(payload), 'used': False, 'revoked': False}
        self.permissions.append(receipt)
        return deepcopy(receipt)

    def revoke(self):
        for permission in self.permissions: permission['revoked'] = True

    def matching_permission(self, payload):
        return next((p for p in reversed(self.permissions) if not p['used'] and not p['revoked']
                     and p['signature'] == signature(payload)), None)

    def mutate(self, kind, target):
        try: payload = self.payload(kind, target)
        except ValueError as exc: return {'ok': False, 'errors': [str(exc)]}
        permission = self.matching_permission(payload)
        before = {'enrollment': list(self.enrolled), 'saved_plans': deepcopy(self.saved), 'waitlists': deepcopy(self.waitlists)}
        errors = []
        sections = payload.get('sections', [])
        if self.paused: errors.append('paused')  # session interruption is respected in both conditions
        if self.controlled and not permission: errors.append('missing_applicable_permission')
        if kind in ('save_plan', 'register_plan'):
            errors += self.rules(sections, include_student=self.controlled)
        if kind == 'register_plan':
            if not self.fixture['registration_open']: errors.append('registration_ticket_closed')
            for section in set(sections) - set(self.enrolled):
                data = self.catalog[section]
                if data['seats_available'] < 1: errors.append('no_seat:' + section)
                if data.get('waitlist_actual', 0) > 0 and not self.waitlists.get(section, {}).get('offer_active'):
                    errors.append('waitlist_offer_required:' + section)
        if kind == 'join_waitlist':
            data = self.catalog[target]
            if target in self.waitlists: errors.append('already_waitlisted')
            if data['waitlist_capacity'] <= data['waitlist_actual']: errors.append('waitlist_full_or_unavailable')
        if kind == 'accept_offer':
            errors.append('no_active_offer' if not self.waitlists.get(target, {}).get('offer_active') else 'offer_acceptance_outside_this_case')
        if not errors:
            if kind == 'save_plan':
                self.saved[target] = {'id': target, 'version': self.saved.get(target, {}).get('version', 0)+1,
                                      'sections': sections, 'credits': self.credits(sections)}
            elif kind == 'register_plan':
                for section in set(self.enrolled) - set(sections): self.catalog[section]['seats_available'] += 1
                for section in set(sections) - set(self.enrolled): self.catalog[section]['seats_available'] -= 1
                self.enrolled = list(sections)
                self.enrollment_version += 1
                self.pending = None
            elif kind == 'join_waitlist':
                self.catalog[target]['waitlist_actual'] += 1
                self.waitlists[target] = {'status': 'waitlisted', 'position': self.catalog[target]['waitlist_actual'], 'offer_active': False}
            if permission: permission['used'] = True
        event = {'action': payload, 'permission_id': permission['id'] if permission else None,
                 'authorized': permission is not None, 'committed': not errors, 'errors': sorted(set(errors)),
                 'before': before, 'after': {'enrollment': list(self.enrolled), 'saved_plans': deepcopy(self.saved), 'waitlists': deepcopy(self.waitlists)}}
        self.audit.append(event)
        return {'ok': not errors, **deepcopy(event)}

    def tool(self, name, target='', sections=None):
        if name == 'read_catalog': return deepcopy(self.catalog)
        if name == 'read_profile': return deepcopy(self.profile)
        if name == 'read_state': return self.snapshot()
        if name == 'draft_plan':
            if not target or len(target) > 24: return {'ok': False, 'errors': ['invalid_plan_id']}
            sections = sorted(sections or [])
            errors = self.rules(sections)
            # Infeasible drafts may be explored; their validity is never hidden.
            if 'unknown_section' in errors: return {'ok': False, 'errors': errors}
            if target in self.drafts and self.drafts[target]['sections'] == sections:
                return {'ok': True, 'draft': deepcopy(self.drafts[target]), 'enrollment_unchanged': True}
            plan = {'id': target, 'version': self.drafts.get(target, {}).get('version', 0)+1,
                    'sections': sections, 'credits': self.credits(sections), 'rule_errors': errors}
            self.drafts[target] = plan
            return {'ok': True, 'draft': deepcopy(plan), 'enrollment_unchanged': True}
        if name == 'propose_registration':
            try:
                payload = self.payload('register_plan', target)
                self.pending = {**payload, 'add': sorted(set(payload['sections'])-set(self.enrolled)),
                                'drop': sorted(set(self.enrolled)-set(payload['sections'])),
                                'rule_errors': self.rules(payload['sections'])}
                return {'ok': True, 'pending': deepcopy(self.pending), 'not_registered': True}
            except ValueError as exc: return {'ok': False, 'errors': [str(exc)]}
        if name in ('save_plan', 'register_plan', 'join_waitlist', 'accept_offer'): return self.mutate(name, target)
        return {'ok': False, 'errors': ['unknown_tool']}
