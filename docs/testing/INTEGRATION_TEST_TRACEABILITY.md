# Integration test traceability

Executed with:

```text
.\.venv\Scripts\python.exe -m pytest tests/integration -q
```

Result: **13 passed, 0 failed**. The first requested command,
`python -m pytest tests/integration -q`, used the system interpreter and could
not import pytest; the repository virtual environment contains the declared
dependency and produced the result above.

| Audit ID | Test | Result | Observed behavior |
|---|---|---:|---|
| IT-EV-01 | `test_it_ev_01_authenticated_event_search_and_modal` | PASS | Authenticated `/app` search renders the matching event, details, modal ID, and Volunteer link. |
| IT-RG-01 | `test_it_rg_01_volunteer_lookup_and_invalid_event` | PASS | Selected event ID is retained in the hidden form, max hours is rendered, and an unknown event returns 404. |
| IT-RG-01 | `test_it_rg_01_registration_persists_once_and_is_listed` | PASS | Valid registration returns confirmation, writes one linked row, increments once, and appears in `/registered-events`. |
| IT-RG-02 | `test_it_rg_02_duplicate_registration_does_not_consume_slot` | PASS | Duplicate returns 400 and leaves one row/count unchanged. |
| IT-RG-03 | `test_it_rg_03_rejected_registration_does_not_write_or_increment[full_event...]` | PASS | Full event returns 400 with no write/count change. |
| IT-RG-03 | `test_it_rg_03_rejected_registration_does_not_write_or_increment[hours_below_minimum...]` | PASS | Zero hours returns 400 with no write/count change. |
| IT-RG-03 | `test_it_rg_03_rejected_registration_does_not_write_or_increment[hours_above_event_limit...]` | PASS | Hours above event limit returns 400 with no write/count change. |
| IT-RG-03 | `test_it_rg_03_rejected_registration_does_not_write_or_increment[unknown_event...]` | PASS | Unknown event returns 400 with no write. |
| IT-RG-04 | `test_it_rg_04_unauthenticated_student_routes_show_no_personal_data_or_mutation` | PASS | All five unauthenticated student-route requests observed status 200 from the custom HTML 401 handler; no personal registration data or mutation was exposed. |
| IT-RG-05 | `test_it_rg_05_unregister_redirects_deletes_registration_and_releases_slot` | PASS | Unregister returns 303, deletes the row, and restores one slot. |
| IT-LB-01 | `test_it_lb_01_public_leaderboard_filters_and_sorts` | PASS | Public leaderboard renders seeded students, combined filters, and descending hours order. |
| IT-LB-02 | `test_it_lb_02_student_modal_has_public_fields_not_registration_details` | PASS | Student modal includes public student fields and excludes registration-specific details. |
| IT-LB-02 | `test_it_lb_02_public_leaderboard_does_not_require_authentication` | PASS | Signed-out filtered leaderboard remains accessible with status 200. |

No concurrency test was added; sequential requests are not treated as
last-slot concurrency evidence.
