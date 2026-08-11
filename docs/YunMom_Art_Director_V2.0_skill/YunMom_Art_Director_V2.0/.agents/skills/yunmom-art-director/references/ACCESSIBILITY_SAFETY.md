# Accessibility, Safety, privacy, and sensitive-state visual contract

## P0 accessibility

Apply one semantic contract on iOS and Android while using native platform components and adapters.

- Support VoiceOver/TalkBack, platform maximum accessibility text and at least 200% scale, logical focus order, non-gesture alternatives, and platform minimum touch targets.
- Reflow or scroll instead of clipping. Risk title, next step, confirmation, destructive action, and care-seeking action must remain visible and reachable.
- Never encode meaning only with color, motion, sound, haptic, location, or character expression.
- Provide qualified contrast in light, dark, and high-contrast modes. Test color-vision differences.
- Preserve semantic role, label, state, value, and action. Decorative images are hidden from accessibility trees; meaningful images get concise labels.
- For Safety reading order, use severity → what happened → what to do now → action. Avoid looping announcements that create panic.
- Every swipe-only journey needs a visible or assistive alternative. Visual minimalism does not excuse hidden essential navigation.

## Reduce Motion

Honor the system preference on both platforms.

- Remove breathing/floating loops, parallax, flashing, particles, long cloud occlusion, and unnecessary zoom/scale.
- Replace spatial motion with short fades or immediate state changes where appropriate.
- Keep risk, error, confirmation, progress, focus, and navigation meaning intact.
- Never make Baby/YunMom motion necessary to understand status.

## Medical Safety and crisis

- Keep Medical Safety/Crisis above error/permission/destructive confirmation, interaction, Mood/Ambient, Task, and decoration in the semantic priority stack.
- A HOME `!` is an entry affordance, not the complete warning. The opened surface must carry explicit severity/action language and accessible actions.
- Never show “current safe/no risk” from stale or incomplete data. Never let a quiet character state imply clinical clearance.
- Do not use Baby distress, YunMom panic, dramatic red worlds, alarms, countdown pressure, or guilt.
- Do not let warmth weaken an R2/R3 action. Do not let MoodCare or persona copy cover crisis routing.
- Do not invent clinical wording. Use MD-approved copy/Rule output and preserve `dismiss != resolve`.

## Widget

- Keep V1 disabled until the user adds it and opts into each permitted field.
- Treat pregnancy week/EDD as sensitive reproductive-health data.
- Permit only approved low-risk fields or generic content. Exclude Risk and “no risk,” report, medication, mood, diary, AI conversation, hospital/doctor, and Gentle Closure details.
- Consume only an encrypted, minimal, read-only local projection. Do not write Event/Command, complete/cancel tasks, close risk, or fetch health state from Gateway.
- Widget interaction may carry only a short-lived opaque deep-link token into the already-installed main App. It must reveal no health data in the URL/intent and may act only after the main App is unlocked and re-authorizes the action.
- Protect the shared container with platform data protection plus application-layer encryption and an extension-specific key. Do not place Event data, attachments, full tasks, installation KEK, or reusable credentials there.
- Exclude the shared projection, extension key, previews, and caches from system backup, device search/indexing, telemetry, logs, Crash/APM payloads, and diagnostic exports.
- Keep lock-screen presentation low sensitivity. Separate Widget authorization from notification authorization.
- Enforce `expires_at` with a maximum of 24 hours; show a generic placeholder after expiry/version mismatch.
- Clear projection, cache, previews, and extension keys after field withdrawal, Widget off, Episode switch/archive/delete, Gentle Closure, or delete-all. Include the Widget in permanent-delete residual scans.

## Gentle Closure and sensitive outcomes

- Use only a user/medical-record-confirmed lifecycle transition into `closure_confirmation_pending`, `quiet_archive`, or `archived`; AI/OCR never triggers it automatically.
- Stop pregnancy countdowns, growth celebration, Baby progress, fruit comparison, future-preparation motion, and stale Widget/notification imagery immediately after confirmed transition.
- Keep Baby visibility a user choice; never default to angel wings, heaven/star ascent, memorial symbolism, or “next pregnancy” promotion.
- Use pre-reviewed restrained copy and low-cognitive-load layouts. Do not expose loss on lock screens or previews.

## Tokens and themes

- Use the versioned semantic Design Token repository as the sole implementation source for color, typography, spacing, radius, elevation, opacity, icon, touch, focus, motion, Ambient, Safety, Crisis, and high-contrast mappings.
- Generate Flutter/Rive/iOS Widget/Android Widget mappings. Do not scatter raw visual constants in production code.
- Themes may change appearance but never severity, reading order, contrast, focus, action reachability, or destructive confirmation.
- Token changes affecting Safety or accessibility require MD plus engineering/QA review and the fixed regression matrix.

## Multiple BabySubjects

- An Episode may contain `1..N BabySubject`. Never reuse one Subject's visual label, report, risk, or stage claim for another.
- Show explicit Subject identity in clinical/detail surfaces and represent unknown attribution as unknown; never guess based on order or confidence.
- Decorative HOME composition may remain calm, but it cannot hide the existence of multiple Subjects where the current task requires subject-specific action.
