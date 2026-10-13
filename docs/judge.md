# student-judge competency report

**Judged at:** 2026-10-11T02:50:00-04:00
**Evidence pass:** re-read all three native Copilot Guide chats for this workspace, current `docs/report.md`, `docs/diagrams/`, and current `docs/wireframes/`; prior `docs/judge.md` ignored

**Student / session:** Student Awards coursework session
**Artifact:** Guide chats for this project and `docs/transcripts/`
**Phases in evidence:** 1–3 (COMP 3613; Phase 5 polish and Phase 6 deploy not reached)

### Totals
| | Count / value |
|--|--|
| Metrics on rubric | 12 (M1–M12) |
| N/A (excluded) | M5, M6, M7, M9 — no Phase 5 implementation/polish opportunity yet |
| Metrics scored | 8 |
| Scoreable max | 32 |
| Awarded total | 32 / 32 |
| **Overall (avg of scored)** | **4.0 / 4** |
| Impression mark | 17 / 20 |

## Scorecard

| ID | Metric | Score / 4 | In avg | Evidence |
|----|--------|----------:|:------:|----------|
| M1 | Phase discipline | 4 | yes | The student opened separate Phase 1, Phase 2, and Phase 3 Guide chats, and the Guide stopped after each design artefact instead of starting app code. |
| M2 | Problem framing | 4 | yes | The student named “Student Awards (incentive system)” and three workflows, then chose the include/shared-use-case decisions and supplied the entity/property list. |
| M3 | Decision ownership | 4 | yes | The student chose “many-to-many through `RegisteredEvent`,” a derived leaderboard, capacity rejection, event lifecycle ownership, and one registration per event. |
| M4 | Artefact-before-code | 4 | yes | The current report contains the project, workflows, UML use-case link, and Phase 3 Mermaid ERD; no app code was started before wireframes. |
| M5 | Verification habit | N/A | no | Phase 5 implementation was not reached, so no student verification opportunity was provided. |
| M6 | Assignment fit | N/A | no | No Phase 5 implementation slice was reached. |
| M7 | Slice explanation | N/A | no | No Phase 5 code-check or implementation-layer explanation was elicited. |
| M8 | Prompt quality | 4 | yes | The student used phase-tagged prompts, including “Use the student-build skill. Phase 3.” |
| M9 | Response to pushback | N/A | no | No implementation or polish mismatch was reached. |
| M10 | Integrity | 4 | yes | No paste-back, answer-seeking, edited-skill, or suspicion flags appeared in the three native chats. |
| M11 | Provenance continuity | 4 | yes | The Phase 3 ERD grows directly from the student’s named workflows and Phase 2 use cases. |
| M12 | Sincerity trajectory | 4 | yes | No suspicion round was needed; the student gave direct answers to relationship, lifecycle, and uniqueness questions. |

## Strengths
- Student-owned project, workflows, entities, and properties are traceable across all three phases.
- The student made concrete relationship decisions instead of accepting an assumed schema.
- The student corrected `eventStatus` placement after the Guide identified that the states described the event lifecycle.
- The Phase 3 report now documents capacity, composite uniqueness, and the derived leaderboard assumption.

## Gaps (priority order)
1. No student-crafted wireframes are present, so Phase 4 coverage and workflow completion cannot be assessed.
2. Phase 5 theming, implementation, student verification, layered code checks, and polish have not been reached.
3. Phase 6 deployment has not been reached; the public URL remains a placeholder.

## Phase gate status
| Phase | Status | Note |
|-------|--------|------|
| 1 | met | Project and three student-owned workflows are in the report. |
| 2 | met | UML JSON/PNG artefact and include/shared/authentication decisions are documented. |
| 3 | met | Student-owned entities, properties, relationships, constraints, and Mermaid ERD are documented. |
| 4 | not met | No wireframe images are present. |
| 5 | N/A | Not reached. |
| 6 | N/A | Not reached; deployment should wait for Phase 5 polish. |

## Recommended next practice
- Create wireframes that cover all three named workflows, then use them to clarify any missing completion path before implementation.

## Integrity note
- Clean

## Provenance flags
- None

## Sincerity log summary
- Blocks found: 0 | max round: 0 | min/mean/final confidence: N/A | trend: none | cleared: yes

## Skips
- Skips: 0/3 used
