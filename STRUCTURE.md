**Kind: artifact.**

Applies: S1 ✅ · README + STRUCTURE ✅ · S6 ✅. S2–S5 do not apply.
Standard: `../command-center/standard/artifact.md`.

The public half of `geometric-abstraction` (private, Kind: studio), where the rounds, ratings and
findings live. This repo holds only what a stranger needs to see and check the finished series:
the 75 paintings, the code that makes each one, the prompts, and `verify/`, which re-renders every
sketch against its PNG (`verify/RESULTS.txt` is the committed run).

Root (closed set): `README.md`, `STRUCTURE.md`, `LICENSE`, `LICENSE-ART.md`, `CITATION.cff`,
`catalog.json`, `index.html` (GitHub Pages viewer).

`catalog.json` was built from the picks in `adamnoonan-xyz/tools/picks/mondrian-decomp.json` and the
round folders in `geometric-abstraction/experiments/`. Painting 28's sketch came from GA-05's training
data, because GA-04b did not keep sketch files.
