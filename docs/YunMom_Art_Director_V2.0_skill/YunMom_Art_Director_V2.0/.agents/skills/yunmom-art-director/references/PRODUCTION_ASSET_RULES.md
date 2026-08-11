# Production Asset Rules

## Concept vs production
### Concept image
May contain illustrative UI and composition cues. Not shipped directly as a functional screen.

### Production asset
Must have a clear runtime role, format, dimensions, alpha/crop behavior, valid aesthetic-Golden parent, provenance, dependency entry, implementation evidence stage, platform/build scope, and privacy classification.

## Character layer contract
When preparing animated YunMom/Baby assets, prefer separable logical layers where feasible:
- yunmom_base
- face_eyes
- face_mouth
- baby
- cloud_puff_left/right or deformable puff region
- star_slots
- prop_slot
- contact_shadow
- highlight/rim layer

Record normalized anchor points rather than hard-coding screen pixels into artwork.

## Runtime ownership
- Flutter owns layout, text, semantic controls, hit targets, navigation.
- Ambient engine owns sky/light/weather/particles.
- Rive/layer animation owns core character motion where supported.
- Raster art owns tactile plush detail when vectorization would damage the look.

## Exports
Keep an editable/high-resolution master and derive runtime exports. Avoid repeatedly recompressing already-compressed images.

## Asset state is multidimensional

- Lifecycle: `candidate`, `finalist`, `provisional`, `aesthetic_golden`, `deprecated`, or `rejected`.
- Freshness: `current`, `stale`, or `stale_contract_conflict` with structured causes.
- Evidence stage: `concept`, `aesthetic_golden`, `integrated`, `matrix_accepted`, or `release_signed`.

Do not collapse these into one “approved/production” flag. User approval can reach `aesthetic_golden` only. Staleness preserves history while blocking new production use. `release_signed` requires the external same-build sign-off package.

## Provenance
Record:
- generation/edit tool
- model when known
- prompt/brief path
- parent references
- creator identity and source kind
- user aesthetic-approval decision bound to asset version/hash
- asset class
- medical source IDs/versions/hashes, range, comparison and qualified review when relevant
- platform/OS/device/Build and evidence hashes for implementation claims

## Rights and commercial-use gate

Record ownership/license status, the exact Provider or third-party terms/version when applicable, commercial and derivative-use permission, attribution requirements, and immutable evidence references. User-provided inspiration is not automatic rights clearance. Unknown/unverified rights may remain concept/reference material but block aesthetic-Golden promotion and every production/release claim. Fonts, icons, stock media, third-party textures, and AI-generated outputs follow the same gate.

## No hidden text
No dynamic medical/pregnancy text embedded into production images.

## Evidence privacy

Use synthetic or irreversibly de-identified data in persisted captures and contact sheets. Never put real health/identity text in asset filenames, prompts, manifests or repository evidence. External health-sensitive image processing requires both an approved exact Provider/model/modality/region/retention path and per-send user confirmation, followed by a stripped-copy workflow; either missing gate fails closed.
