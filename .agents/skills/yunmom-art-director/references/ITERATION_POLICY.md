# Iteration Policy

## Internal refinement
Do not expose raw generations to the user. Iterate internally while there are clear, actionable defects.

Suggested pattern for an important round:
1. broad but controlled exploration
2. hard-gate cull
3. peer review
4. focused refinement
5. integrated screenshot check
6. finalist curation

## Avoid thrashing
If three focused attempts fail for the same identifiable reason, stop random regeneration. Diagnose the root cause: bad reference role, wrong composition, unsuitable production technique, or conflicting invariant. Change the process, not just the seed/prompt wording.

## Preserve accepted qualities
When user feedback asks for one change, freeze all unrelated approved qualities. Example: “B 的脸再温柔一点” must not also change silhouette, fur, palette, Baby Nest, camera, or lighting unless technically unavoidable.

## Finalist diversity
Finalists should offer meaningful but bounded choices. After identity lock, do not present radically different art styles as A/B/C.
