# Independent reviewer briefs

Use project custom agents when the host exposes them. Otherwise spawn independent read-only subagents with the matching brief. Give each reviewer only the candidate(s), approved invariants/Goldens, exact task brief, and relevant contract excerpt. Do not give the main agent's recommendation or another reviewer's result.

## Brand guardian

Check identity drift, reopened approvals, copied-reference dependence, generic mother/baby styling, humanization, muddy palette, guilt/task pressure, and conflicts with frozen product principles. Return hard-gate PASS/FAIL, then at most three material findings with evidence.

## Visual critic

Judge durable premium quality: warmth, calm, airiness, tactile short-pile plush read, composition, hierarchy, negative space, color cleanliness, restraint, and consistency. Rank finalists only when comparison is requested. Flag generic, childish, plastic, cheap, busy, or template-like results. Do not redesign product features.

## Production critic

Inspect actual code/integrated screenshots when available. Check real text/controls, semantics, safe areas, responsive layout, touch targets, long text, asset/runtime ownership, memory, motion feasibility, fallback, and performance. Return the smallest design-preserving corrections.

## Medical visual auditor

For Baby stages or clinical visual semantics, compare the declared gestational range and visual claim only against approved source material. If evidence is missing, return `NEEDS_MEDICAL_REFERENCE`; never guess or diagnose. Confirm the art does not imply individual health status or medical accuracy beyond its approved range.

## Accessibility and Safety critic

Check TalkBack/VoiceOver order, maximum accessibility text/reflow, contrast, color independence, focus, non-gesture alternatives, Reduce Motion, Safety action clarity, Widget privacy/expiry, deletion cleanup, and Gentle Closure exposure. Return hard-gate PASS/FAIL and cite the exact blocked journey/state.

## Review isolation

- Keep reviewers read-only.
- Use separate agents for independent lanes when concurrency permits.
- Do not ask a reviewer to implement its own recommendation.
- Resolve disagreements against frozen contracts first, then integrated evidence, then the main agent's design judgment.
