# Round Workflow — user selection without user burden

## Philosophy
The user should never review raw generation noise. Codex acts as curator before the user sees anything.

## Standard round
1. Define the single decision goal of this round.
2. Hold already-approved dimensions constant.
3. Generate 4–6 internal candidates when exploration is needed.
4. Hard-gate invalid candidates.
5. Peer-review the survivors.
6. Refine if necessary.
7. Show at most 3 finalists A/B/C.
8. Give one recommended option.
9. Ask only: which feels most right / what single quality should change?
10. Record feedback before doing more work.

## Do not overwhelm
Never ask the user to choose:
- exact hex values
- radius values
- blur/shadow parameters
- animation milliseconds
- asset layer structures
- shader parameters
- export dimensions

## Feedback interpretation
- “A最好 / 我喜欢A” → A is preferred, not automatically frozen unless wording clearly approves finality.
- “A最好，脸再柔和” → A becomes provisional parent; only face softness changes next round.
- “就这个 / 定了 / 按这个继续” → promote the named artifact to an immutable aesthetic Golden after its required reviews. This is not implementation acceptance or release approval.
- “都不对” → reject the round; identify common failure and reopen only the necessary dimensions.

## After approval
Automatically:
- version and promote an aesthetic Golden;
- update Decision Log;
- update DESIGN_STATE;
- generate/update Style Lock Sheet where relevant;
- propose a governed Token/grammar version if the aesthetic Golden is system-defining; do not directly rewrite active implementation Tokens;
- mark dependent assets stale if a parent changed.

If a contract, professional review, or verification evidence changed, mark affected work `stale_contract_conflict` even if the user still likes it. Never use creative approval to bypass a domain No-Go.
