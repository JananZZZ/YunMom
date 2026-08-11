# Evidence and visual QA

Match every claim to the strongest completed evidence tier.

| Tier | Evidence | Allowed claim |
|---|---|---|
| 0 | Brief, sketch, generated concept | concept/direction only |
| 1 | Isolated reviewed asset with provenance | asset candidate/finalist |
| 2 | Asset integrated into a faithful screen frame | integrated direction, not implementation acceptance |
| 3 | Running implementation screenshot plus code/state inspection bound to platform/build | implemented on tested target |
| 4 | Required platform/device/state/accessibility/performance matrix | accepted for that matrix |
| 5 | Same-build signed release evidence | release-ready only after all professional gates |

Never skip from Tier 0/1 to “production-ready.”

## Minimum review packet

For a user-authorized create/edit/implement or promotion workflow, record:

- task/asset ID, impact class, current Gate, parent Goldens, decision ID;
- source Build/commit when code exists;
- viewport/device, OS, pixel ratio, theme, locale, text scale, Reduce Motion and accessibility mode;
- state inputs and whether data is synthetic;
- screenshot/artifact path and SHA-256;
- hard-gate results, reviewer records, known limitations, and next evidence tier.

Store only synthetic/de-identified screen captures as `visual/reviews/screens/<space>_<state>_<platform>_<viewport>_vNN.png` and review records under `visual/reviews/`. In a pure review, critique, audit, or report, do not create these files; return the structured findings in the response and identify any missing evidence instead.

## Visual-evidence privacy gate

- Use synthetic or irreversibly de-identified data for persistent screenshots, videos, prompts, contact sheets, manifests, and diagnostic evidence.
- Never persist real health content, identity, reports, hospital/doctor details, account identifiers, prompt/response bodies, or visible private notifications in the repository or filenames.
- Apply the same rule to medical-source archives, reviewer credentials, and signed attestations. Each local attachment needs an exact sibling provenance sidecar; a file hash without privacy classification and authorization is not admissible evidence.
- Do not enable Session Replay or automatic screenshot/recording telemetry.
- A health-sensitive file may go to an external image/AI Provider only when the exact Provider legal entity, model/version and modality, region/data path, retention/training terms, and subprocessors are already approved on the China allowlist **and** the user gives per-send confirmation of the file, purpose, Provider, and path. Confirmation cannot waive a missing Provider approval. Use a copy stripped of unnecessary EXIF; never queue, silently retry, or auto-switch Provider.
- Treat temporary capture/export files as deletion-scope data and clean them after the task.

## UI state coverage

Test relevant states, not only the happy path:

- loading, empty, content, long content, error, offline, permission denied, pending/cancelled, stale, disabled;
- Normal, Silent Day, R0–R3/Safety entry and detail, voice/camera/AI Partial/Receipt;
- Consent, withdrawal, destructive confirmation, delete completion/failure recovery;
- Gentle Closure and Episode switch/archive/delete;
- Widget disabled/opt-in/expired/revoked/offline/deleted;
- light, dark, high contrast, color-vision checks, system Reduce Motion;
- normal and platform maximum accessibility text, including at least 200%;
- TalkBack/VoiceOver focus/read order and non-gesture navigation.

## Viewport and device evidence

During development, use available devices and emulators honestly. Before public release, bind evidence to the signed OS/device matrix with at least an upper-tier and lowest-supported real device on each platform. Android evidence never substitutes for iOS.

Protect focal hierarchy on compact and large phones. Never shrink touch targets or truncate Safety actions to preserve screenshot similarity.

## Visual regression

- Keep deterministic states, data, font configuration, viewport, and animation frame.
- Use semantic-region assertions before perceptual comparison.
- Treat ≥0.99 perceptual similarity as a configured regression threshold only where the release contract requires it.
- Do not Mask Risk, Receipt, text, focus, navigation, confirmation, or Widget privacy regions.
- A visually similar screen still fails if semantics, focus, contrast, privacy, or action reachability regress.

## Performance

Measure on named Release builds and devices. Preserve the frozen frame-time, cold-start, crash-free, and offline P0 thresholds. A concept animation is not feasible until the runtime owner, memory footprint, fallback, pause/background behavior, and Reduce Motion behavior are known.

## Completion report

End each visual task with:

1. what changed and where;
2. which hard gates and states were tested;
3. the current evidence tier;
4. pending platform, medical, legal, security, accessibility, or production evidence;
5. whether visual registries/state were updated;
6. the exact claim: concept, aesthetic Golden, integrated, matrix accepted, or release signed.
