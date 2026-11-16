# Banner workflow observations

Observed November 15, 2026 through the normal browser interface. This records interface structure, not the student's private plan contents. No plan rows, notes, preferences, enrollment, or waitlists were changed, and no Save Plan or registration Submit action was performed.

Entry point: https://nubanner.neu.edu/StudentRegistrationSsb/ssb/registration

## Directly observed in the current interface

- The landing page separates Prepare for Registration, Plan Ahead, Register for Classes, Browse Classes, View Registration Information, and Browse Course Catalog.
- Browse Classes provides term-specific section search. The inspected term was Spring 2027. Advanced filters include campus, level, instructional method, schedule type, credit range, meeting days/times, and Open Sections Only.
- Section details distinguish the course number, section number, five-digit CRN, term, credits, campus, schedule type, and instructional method. These identifiers are not interchangeable.
- Detail tabs expose restrictions, meeting information, enrollment/waitlist information, corequisites, prerequisites, mutual exclusions, cross listings, and linked sections. Their presence is observed; complete enforcement semantics were not tested.
- Enrollment/Waitlist reports separate enrollment actual/maximum/available counts and waitlist capacity/actual/available counts. One inspected public section had zero waitlist capacity; another had a positive capacity. A free enrollment count alone is insufficient to infer a particular student's right to register.
- A prerequisite table can express alternatives with OR and minimum grades. The prototype's flat list of completed prerequisites is a simplification.
- Meeting information includes dates, day patterns, start/end times, and location. A course can have multiple meetings, and some sections have no ordinary weekly meeting pattern.
- Plan Ahead first selects a term and then a saved plan. The inspected screen allowed up to five plans for that term and identified a preferred plan. This is an observed configuration, not a universal policy constant.
- The plan editor combines class search, a weekly calendar, schedule details, planned-course rows, notes, per-row actions, total planned hours, and Save Plan. Rows are labeled Planned. Opening the action menu revealed None and Delete; no action was selected.
- Register for Classes follows a separate term-selection path. The signed-in session was stopped by a time-ticket eligibility message. The actual registration form beyond that gate was not inspected live.

## Documented behavior that was not exercised live

The registrar's registration guide describes moving selections into a pending summary, then submitting them to register. It also describes a conditional add/drop transaction that preserves existing enrollment when the replacement cannot be added. Source: [Registering for Classes, pages 5–7](https://registrar.northeastern.edu/wp-content/uploads/sites/9/Registration-Document-New.pdf).

The registrar's waitlist instructions describe joining a waitlist as a separate action. The first student receives a notification when offered a seat and has a documented 24-hour response window. Joining the queue is not registration, and watching for openings is not permission to join or accept an offer. Source: [Waitlist Instructions, pages 3–5](https://registrar.northeastern.edu/wp-content/uploads/sites/9/Waitlist-Document-1.pdf).

These guides contain older interface material. Treat documented deadlines and limits as configurable scenario rules and verify current applicability before any real integration. The older [planning guide](https://registrar.northeastern.edu/wp-content/uploads/sites/9/Planning-Document-1.pdf) mentions three plans, while the current inspected screen allowed five; current UI evidence takes precedence for that observation.

## Consequences for the mock environment

Represent previewed alternatives, saved plans, staged registration requests, actual enrollment, and waitlist membership separately. Give each consequential action its own explicit permission scope. Include eligibility/time-ticket checks and versioned plans. Use fictional academic records, not the private plan inspected in the browser. The next case should focus on changed approval scope across a longer interaction, without assuming a competitive seat race for a waitlisted section.

## Unverified areas

No real add/drop, waitlist join, queue position, notification delivery, offer acceptance, or failure transaction was exercised. No full academic audit or all-college rule set was inspected. The simulator must label these as mocked behaviors and scope its claims accordingly.
