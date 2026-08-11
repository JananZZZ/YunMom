# UI System

## Global structure
Primary spaces are HOME, MEMORY, CARE, KNOW; AI Overlay floats above them. No bottom tab.

## HOME hierarchy — active/applicable Episode
1. Pregnancy Time above the character
2. YunMom + Baby as dominant visual focus
3. Ambient sky/light/weather
4. Task stars if needed
5. Contract-compliant Safety entry affordance only when active; full severity and action live in the controlled Safety surface
6. Temporary interaction text only when needed

HOME must not accumulate cards. Most persistent text should disappear unless it has immediate value.

For confirmed Gentle Closure, quiet archive, or any state where pregnancy progress is no longer appropriate, Pregnancy Time, growth/Baby progress, celebration, and future-pregnancy preparation are removed rather than forced into this hierarchy. Baby visibility is user-controlled. The resulting restrained HOME is a first-class state, not a failed version of the active hierarchy.

## CARE / Soft Bento
- Use a weighted Bento composition, not a uniform 2×3 utility grid.
- First level has six domains: 产检与报告 / 我的孕期 / 每天的照料 / 未来准备 / 小工具 / 爸爸也在.
- Positions stay stable for muscle memory.
- Importance may change light, star, or subtle elevation, not layout position.
- No unread badges or task counts.

## MEMORY
- Memory River first; Calendar alternate view.
- Medical records coexist with warm memories but do not make the page feel like a hospital chart.

## KNOW
- First view: “这周值得知道的 3 件事”.
- Avoid addictive infinite-scroll aesthetics.

## AI Overlay
- Minimal cloud-like layer with voice, camera, text.
- AI action Receipt exposes the actual Command/Event result, correction/undo capability, and deletion scope. Do not use one generic trash action for Undo, hide, and permanent purge.
- Do not expose model/tool technical complexity in the everyday UI.

## Production UI rule
Generated mockups guide composition and material. Rebuild dynamic UI with real Flutter layout and text. Do not ship screenshots as UI.

## Semantic and accessibility rule
Use one cross-platform journey/semantic contract with native platform adapters. Support TalkBack/VoiceOver, platform maximum accessibility text and at least 200%, reflow, logical focus, minimum targets, non-gesture navigation, high contrast, color independence, and system Reduce Motion on every P0 flow. Visual minimalism never removes an essential label, action, or alternate path.

## Safety and sensitive surfaces
Safety exposes severity, what happened, what to do now, and the action with explicit text, a non-decorative icon, correct accessibility state, and a reachable control; a HOME `!` can only be an entry affordance. `dismiss` does not resolve risk, and R0 is not a promise of health. Widget is default-off, per-field opt-in, read-only, low sensitivity, and never a Safety channel. Gentle Closure removes stale countdown, growth, Baby-progress, notification, preview, and Widget presentation immediately after a confirmed transition.

## Episode and multiple subjects
Render `1..N BabySubject` without implying that one subject's data applies to another. Keep fetus-specific facts attached to a named/numbered Subject, keep mother data at Episode level, and represent uncertain attribution explicitly. Do not force a single-Baby composition into a multi-subject clinical view.

## Typography
Prefer platform/system Chinese typography initially unless a properly licensed typeface is intentionally selected. Never bundle unlicensed fonts merely for visual similarity.

## Responsive quality
Protect focal hierarchy across common compact and large phones. Do not shrink interactive targets to preserve a concept screenshot.
