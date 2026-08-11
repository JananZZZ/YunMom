# Static / Dynamic Asset Matrix

## Purpose
Choose the production technique that preserves YunMom's plush quality without turning the app into a heavy real-time 3D scene.

| Asset | Concept generation | Production source | Runtime owner | Notes |
|---|---|---|---|---|
| YunMom Master | Image generation/editing | high-res master + separable layers where feasible | Rive/layered Flutter | Identity must come from a current aesthetic Golden |
| Baby stage Master | Image generation/editing + medical gate | high-res master + scoped stage/source metadata | Rive/layered Flutter | Never self-certify; Golden requires structured medical verification |
| Face micro-expression | edit/master derivation | small layer/sprite/vector | Rive/Flutter | Preserve face proportions |
| Cloud Puff | edit/master derivation | layer/mask/deform region | Rive/Flutter | No human hand |
| Stars | image/vector exploration | optimized transparent asset/vector | Flutter/Rive | state uses semantic Tokens plus non-color semantics where meaningful |
| Fruit/props | image generation | optimized transparent assets | Flutter/Rive | decorative only |
| Sky/time gradients | concept references optional | code tokens/shaders | Flutter shader | do not ship a giant sky screenshot |
| Rain/snow/particles | motion concept optional | procedural parameters | Flutter/particle engine | distant, calm |
| Bento icons | image exploration | simplified production icon/vector/raster | Flutter | no emoji production dependency |
| Full UI mockup | image generation useful | NOT a production screen | reference only | rebuild as real Flutter UI |
| Hero motion concept | storyboard/video reference optional | state chart + approved layer assets | Rive/Flutter | generated video is not default runtime |
| Pregnancy recap cinematic | image/video generation optional | exported media | export renderer | separate from live UI |

## Rule of thumb
- If it contains dynamic text, health data, buttons, accessibility semantics, or layout that changes: Flutter owns it.
- If it defines plush identity/material: a current aesthetic Golden owns the creative identity, while implementation values still come from semantic Tokens.
- If it is continuously changing ambience: procedural runtime owns it.
- If it is character motion: Rive/layered animation owns it when possible.
