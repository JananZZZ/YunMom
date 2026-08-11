# Motion System

## Principle
Motion is the breathing of the world, not decoration competing for attention.

## Rhythm
- Micro feedback roughly 150–350ms
- Element transitions roughly 350–700ms
- Space transitions roughly 600–1000ms
- Emotional milestones roughly 1.2–2.5s
- Ambient loops roughly 8–30s
These are starting ranges; tune in running UI.

## One moving focus
If Pregnancy Time morphs, characters remain quiet. If a star completes, background stays calm. If Safety Card opens, ambient activity recedes.

## System Reduce Motion is mandatory
When the platform Reduce Motion preference is active, remove breathing/floating loops, parallax, flashing, particles, long cloud occlusion, and unnecessary zoom/scale. Prefer immediate changes or short fades. Preserve state, focus, error, confirmation, navigation, and Safety meaning. Never require character motion to understand an action or risk.

## Production strategy
1. Procedural Flutter/shader for sky, gradients, particles, parallax, subtle weather.
2. Rive/layered 2.5D for YunMom/Baby core states when authoring pipeline is available.
3. Small sprite/image sequences only for rare plush effects when they outperform procedural approaches.
4. Generated video may be used as motion reference or exported recap material, not as the default runtime character system.

## Rive honesty rule
Do not invent a `.riv` file without actual supported authoring tooling. Instead output the layer contract, state chart, triggers, timings, and a faithful runtime prototype that can later be ported into Rive.

## Candidate state vocabulary

YunMom may use: idle, blink, look_at_baby, look_at_user, listen, think, cloud_puff, hold_star, prop_interaction, sleepy/night, silent_day. Implement only states that serve the current journey and have a static/Reduce Motion equivalent.

Baby motion is never a universal required set. Sleep, breathing, curl, stretch, turn, gentle_kick, touch_cloud, nestle, or subtle wake may be used only when the specific Baby anchor declares the applicable gestational range/Subject context and the motion has source-bound qualified medical visual verification. Never use motion frequency, absence, vigor, or timing to imply an individual fetus's health, viability, movement pattern, or Safety state. Unknown attribution stays unknown for multiple BabySubjects. Disable or replace Baby motion whenever its range is inapplicable, evidence is stale, the user hides Baby, or Gentle Closure/sensitive-outcome rules apply.

## Weather
Rain remains mostly distant; no thunder/lightning. Snow is gentle and non-seasonal. Daypart transitions interpolate rather than switch at exact clock boundaries.

## Accessibility and performance evidence
Define a static or reduced-motion equivalent for every state. Test motion on the named upper-tier and lowest-supported devices; pause nonessential animation in background, under thermal/memory pressure, and when the surface is obscured. Do not claim Rive feasibility without a real authoring/runtime path and measured asset cost.
