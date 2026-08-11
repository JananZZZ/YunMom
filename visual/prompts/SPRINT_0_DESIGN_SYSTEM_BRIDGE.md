# Visual Task Contract — Sprint 0 Design-System Bridge

## Control

- Task / asset ID: `VIS-S0-DESIGN-BRIDGE-001`
- Request mode: implement
- Current Gate: `G1_YUNMOM_MASTER`
- Impact class: A
- Evidence stage target: concept
- Target platform / Build: Android-first Flutter workspace; iOS contract present; no Release Build yet
- Frozen decision IDs: `BND-003`, `A11Y-001`, `A11Y-002`, `A11Y-003`, `TOK-001`, `TOK-002`, `TOK-003`, `MAT-001`

## Purpose and journey

Create the code boundary that prevents provisional YunMom Design Tokens from
being mistaken for production-ready constants while the Flutter workspace is
being established. The only current surface is an explicitly development-only
Sprint 0 boot screen.

## Reference roles

- Inspiration reference: none
- Identity Golden: none approved
- Baby stage Golden: not applicable
- Screen Golden: none approved
- Style Lock: none approved
- Parent/dependency asset IDs: none

## Must preserve

The machine-readable Token Bundle remains the sole future implementation
source. `implementation_ready: false` fails closed. Android implementation does
not waive iOS parity, accessibility, Medical Safety, privacy, or release gates.

## Allowed to change

Package boundaries, bootstrap diagnostics, build wiring, and tests. No brand
palette, typography, illustration, motion, medical semantics, or production
screen composition is being selected.

## Composition, material and emotion

Not applicable to production art. The boot surface remains structurally plain,
honest, readable, and unmistakably development-only.

## Forbidden

No production UI claim, no raw YunMom brand constants in app code, no generated
full-screen mockup, no real health data, no Risk or Gentle Closure simulation,
and no aesthetic-Golden promotion.

## Privacy and egress

- Data classification: public_product
- Content origin: synthetic
- Persistent evidence allowed: yes
- External egress: prohibited
- Approved Provider path, if egress applies: not applicable
- Per-send receipt, if egress applies: not applicable
- Cleanup scope: repository source and ordinary generated build/cache output

## Rights

- Status: owned
- Commercial use allowed: yes
- Derivative use allowed: yes
- Attribution: not required
- Rights evidence: `RIGHTS-OWNED:user-authorized-project-implementation-2026-08-11`

## Production requirements

Real Flutter widgets own text, semantics, layout, and focus. The bridge exposes
a fail-closed readiness check only; accepted generated platform mappings remain
future G4 work.

## Validation matrix

Run formatting, static analysis, package tests, and the bootstrap widget test.
Full Android/iOS/Widget, screen-reader, maximum text, Reduce Motion, Safety, and
Gentle Closure matrices remain outside this concept-stage foundation.

## Evidence and provenance

Source files and tests in the Sprint 0 workspace are the current evidence. No
screenshots, external Provider calls, real health content, or release evidence
are created by this task.
