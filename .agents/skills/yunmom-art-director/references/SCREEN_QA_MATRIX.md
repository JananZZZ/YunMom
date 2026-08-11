# Integrated Screen QA Matrix

A screen is not approved solely because one screenshot looks beautiful.

## Required viewport families
At minimum test:
- compact phone around 360×800 logical px
- common Android around 412×915 logical px
- common iPhone-class 6.1-inch portrait
- large iPhone-class portrait

Use actual emulator/device profiles available in the project; do not distort aspect ratios to mimic them.

## Text scale
Check normal and platform maximum accessibility text, with at least 200% scaling. Reflow or scroll; never clip or hide Risk titles, next actions, consent, confirmation, delete, or care-seeking actions.

## Core visual states
HOME:
- normal clear day
- single-subject and multi-BabySubject compositions without cross-subject implication
- Silent Day
- sunset/night
- rain
- task star
- R0–R3 entry and controlled Safety detail, including `dismiss != resolve`
- AI listening
- camera drag target

CARE:
- default Bento
- one highlighted/relevant domain

MEMORY:
- Timeline
- Calendar
- subject-specific record and unknown-attribution presentation when applicable

KNOW:
- weekly 3 cards

AI:
- empty overlay
- short conversation
- action Receipt with accurate result, correction/undo availability, and deletion scope

WIDGET:
- not added/default off
- per-field opt-in
- authorized low-sensitive content
- expired/version mismatch placeholder
- revoked, Episode switched/archived/deleted, Gentle Closure, and delete-all cleared state

SYSTEM:
- light, dark, and high contrast
- color-vision checks
- Reduce Motion
- TalkBack/VoiceOver reading and focus order
- non-gesture alternatives
- offline, permission denied, failure, pending, cancellation, and stale data
- same-device DadEntry, category authorization, withdrawal, and non-owner suggestion states when applicable
- `active`, `delivery_completed`, `closure_confirmation_pending`, `quiet_archive`, and `archived` presentation boundaries

## Review questions
- In an active/applicable Episode, is Pregnancy Time still clearly above the character? In confirmed Gentle Closure/quiet archive, is it completely absent rather than visually preserved?
- Is YunMom still the dominant focal object where the active hierarchy applies, and does the closure state avoid forcing Baby visibility or progress imagery?
- Does any compact viewport turn the page into a dashboard?
- Are hit targets large enough despite visually tiny controls?
- Are safe areas respected?
- Does text wrapping preserve calm spacing?
- Does the Safety entry remain visible without becoming the only carrier of severity or action?
- Do weather/ambient layers reduce readability?
- Is the screen still recognizably YunMom with motion disabled/frozen on one frame?
- Does every Safety/Crisis state carry explicit text, icon, semantic state, and reachable action without relying on color or motion?
- Do consent, deletion, and Gentle Closure remain complete at maximum text scale and with a screen reader?
- Does Widget expose only currently authorized fields and clear every stale cache/preview path?

## Screenshot naming
`<space>_<state>_<platform>_<viewport>_vNN.png`

Bind the exact source Tag/Build hash, OS/device, locale, text scale, accessibility mode, and screenshot SHA-256 in the associated review/evidence record rather than extending filenames with sensitive or unstable data.
In a user-authorized modifying or promotion workflow, store review captures under `visual/reviews/screens/`. In a pure review, critique, audit, or report, return findings without saving captures or changing project state.

Only synthetic or irreversibly de-identified content may be persisted in repository screenshots. Never place real health text, identity, report content, hospital/doctor data, account IDs, or visible private notifications in filenames or captures.

Bind release claims to the named device/OS/Build matrix. Emulator evidence may supplement but never replace required Android/iOS real-device Safety, deletion, backup, accessibility, and performance evidence.
