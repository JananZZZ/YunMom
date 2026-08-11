# Image Generation Playbook

## Reference hierarchy
Every image task must assign explicit roles to references:
1. User inspiration reference → mood/material/comfort only; not an identity lock.
2. Current YunMom aesthetic Golden → identity lock.
3. Current, medically verified Baby-stage aesthetic Golden → scoped stage/character lock.
4. Current screen aesthetic Golden → composition/hierarchy lock.
5. Style Lock Sheet → palette/material/lighting lock.

Never silently treat an inspiration image as the exact character to reproduce.

## Edit-first after approval
Once a Golden character exists:
- preserve silhouette, face proportions, plush material, nest relationship, camera language;
- edit only the requested state/pose/prop/lighting;
- do not regenerate a new character from prose unless the Master itself is intentionally being redesigned.

## Candidate strategy
Before a Master is approved, create meaningful exploration internally. Variants should differ along 1–3 controlled dimensions (e.g. silhouette softness, face spacing, nest depth), not become unrelated art styles.

After a Master is approved, variants should be tightly controlled.

## Prompt structure
- Asset purpose
- Reference roles
- Immutable identity requirements
- Allowed variation
- Composition
- Material/light
- Emotional goal
- Explicit “do not change” list
- Negative/forbidden traits
- Production/background/alpha needs

## Model and data-path provenance
Prefer a pinned, approved image model/version when the tool exposes one and record the actual Provider, model/version, tool, input hashes, purpose, prompt path, output hash, and parent assets. Never invent or assume a snapshot ID the tool did not expose.

Before any health-sensitive file leaves the device, first verify that the exact Provider legal entity, model/version and modality, region/data path, retention/training terms, and subprocessors are approved on the current China allowlist. Then show file, purpose, Provider and path and obtain explicit per-send confirmation. User confirmation never substitutes for Provider/legal approval. If any path fact is unknown or unapproved, fail closed to local processing or an irreversibly de-identified copy. Remove unnecessary EXIF; never queue, silently retry, or auto-switch Provider. Repository prompts and outputs use synthetic/de-identified content.

## No text-in-art rule
Do not generate production UI text inside character/background imagery. Text in concept mockups is illustrative only and must be rebuilt in Flutter.

## Quality loop
Generate → inspect → crop/alpha/edge/material check → integrate → screenshot → critique → controlled edit.
