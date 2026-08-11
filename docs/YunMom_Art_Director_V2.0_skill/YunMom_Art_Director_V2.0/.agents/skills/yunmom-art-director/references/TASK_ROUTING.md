# Task routing

Choose the smallest workflow that fully covers the request.

| Task signal | Route | Required output |
|---|---|---|
| “设计/重做/完善页面或组件” | Inspect code and target states → UI System → Accessibility/Safety → implement real UI → capture and critique | Code, state coverage, responsive/a11y evidence |
| “生成角色/插画/图标/道具” | Inspect reference roles → Character/Art Direction → ImageGen playbook → asset registration → integrated check | Versioned asset, provenance, parent lineage |
| “修改这张图” | View target image first → preserve Golden locks → image edit → edge/alpha/material check | Controlled derivative, not a new identity |
| “评价截图/审美把关” | View screenshot at original detail → contract hard gates → independent critique when S/A → prioritized corrections | Evidence-led verdict; no edits unless requested |
| “动效/Rive/天气/Ambient” | Motion + static/dynamic matrix → runtime ownership → Reduce Motion/fallback → performance test | State chart, implementation, fallback evidence |
| “Widget” | Contract precedence → Widget privacy allowlist → native platform constraints → deletion/expiry tests | Read-only opt-in projection and lifecycle evidence |
| “Safety/危机/Gentle Closure” | Contract precedence → Accessibility/Safety → MD/ETHICS-approved semantics → state matrix | Explicit text/action semantics; no decorative override |
| “提取设计系统/Token” | Approved Golden inputs → extraction reference → versioned semantic tokens → generator/lint/goldens | One Token SSOT, generated platform mappings |
| “做 A/B/C 候选” | One decision goal → controlled internal exploration → hard-gate → independent review → at most 3 finalists | Recommended finalist set, bounded differences |
| “按这个继续/定稿” | Interpret approval → record decision → review gate check → immutable aesthetic-Golden promotion → stale dependents | Aesthetic Golden record, state update, dependency impact; never release approval |

## Tool routing

- Use the platform image generation/editing tool for bitmap generation or edits.
- Use image inspection for every supplied/local image before editing or judging it.
- Use the real app and browser/device testing tools for integrated UI evidence when available.
- Use subagents only for independent, bounded review lanes; keep the main agent responsible for source reading, design synthesis, edits, and final claims.
- Resolve scripts from `SKILL_DIR`: use `<SKILL_DIR>/scripts/visual_ops.py --project-root <PROJECT_ROOT>` for machine state and `<SKILL_DIR>/scripts/build_contact_sheet.py --project-root <PROJECT_ROOT>` for review sheets. Follow [STATE_TOOL_REFERENCE.md](STATE_TOOL_REFERENCE.md); do not reconstruct mutation JSON by hand.

Do not invoke image generation for a task that is better solved with real layout/code, and do not use generated screenshots as a substitute for production UI.
