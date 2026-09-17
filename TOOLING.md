# Tooling map

Where to start looking for a real library implementing a given T1 primitive or T2 pairing. High-level pointers, not an evaluation.

> **What this is and isn't.** This is a starting-points index, not a vetted or endorsed list, and it is **not maintained on a regular schedule**. No version numbers are pinned deliberately — check each project's own documentation for what's current. This is a different, lighter regime from the `tooling_candidates` field on a Privacy Card: submitting a tool *into a card* carries the endorsement expectations set out in [CONTRIBUTING.md](CONTRIBUTING.md) (deployment or peer-review evidence required); this document is just a map of where to look, and treats every entry as a starting point to verify yourself, not a recommendation. **Corrections, additions, and removals are welcome as pull requests** — this page will drift out of date faster than the rest of the repository, and that's expected rather than a problem to solve once.

---

## In closer focus

Three libraries get fuller entries here because they matter beyond a pointer: two are already load-bearing in the companion [stepwise-privacy-cards](https://github.com/j0hn-s/stepwise-privacy-cards) evaluation harness, and the third is a real alternative worth understanding before choosing between them.

### Flower — `FL`

**[flower.ai](https://flower.ai/)** — federated-learning framework, framework-agnostic on the ML side (works with PyTorch, TensorFlow, NumPy, JAX). **Already in active use**: it's the FL substrate in stepwise-privacy-cards' own `flta_eval/fl.py` (`flwr.client`, `flwr.server`, `flwr.simulation` used directly, not just cited). If you're extending the FL-shaped worked examples (`S-01`, `S-03`) or building [the stepwise-privacy-cards roadmap's new items](https://github.com/j0hn-s/stepwise-privacy-cards/blob/main/docs/STEPWISE_CARDS_ROADMAP.md), this is the library already wired into the harness — start there rather than introducing a second FL framework unless there's a specific reason to.

### OpenDP — `DP-C`, `DP-L`

**[opendp.org](https://opendp.org/)** — a library of statistical DP mechanisms (mean, count, sum, quantile, histogram) with a formally-verified core. **Not currently used in the harness** — DP-SGD training in `flta_eval/fl.py` uses Opacus instead. That's not a gap so much as a division of labour worth being explicit about: Opacus is built for gradient-based training (DP-SGD on a model); OpenDP is built for exactly the aggregate-statistic shape (mean, count, a survival-curve-adjacent quantity) that the OXFORDIA-inspired worked example and the [stepwise-privacy-cards roadmap's item 8](https://github.com/j0hn-s/stepwise-privacy-cards/blob/main/docs/STEPWISE_CARDS_ROADMAP.md) (MPC/DP trialled separately, non-FL statistical computation) actually need. If that work goes ahead, OpenDP — not Opacus — is the natural fit for the DP-alone track.

### NVIDIA FLARE — `FL`

**[nvflare.readthedocs.io](https://nvflare.readthedocs.io/)** — federated-learning framework with a stronger enterprise/healthcare deployment footprint than Flower; it's the platform behind NHS FLIP (Soltan et al. 2024, already cited in `data/pairings.yaml` `S-01`). **Not currently used in code here** — it's cited as a real-world deployment precedent, and as an example card's `tooling_candidates` entry, but the harness itself runs on Flower. Worth knowing about specifically as the more production/healthcare-oriented alternative if a deployment story (rather than a research harness) is the goal — which is closer to what OXFORDIA is actually trying to build.

---

## Everything else — pointers only

| Primitive / pairing | Starting points |
|---|---|
| `MPC` | [MP-SPDZ](https://github.com/data61/MP-SPDZ) (already cited in `P-02`, `P-05`), [CrypTen](https://github.com/facebookresearch/CrypTen), [PySyft](https://github.com/OpenMined/PySyft) — PySyft's "structured transparency" design (compute on data you can't directly see) is arguably the closest existing library philosophy to a Solid-pod-federated architecture like OXFORDIA's, worth a specific look |
| `HE` | [Microsoft SEAL](https://github.com/microsoft/SEAL), [TenSEAL](https://github.com/OpenMined/TenSEAL) (SEAL + PyTorch/NumPy glue), [Concrete](https://github.com/zama-ai/concrete) (Zama), [HElib](https://github.com/homenc/HElib) (already cited in `HE`'s `key_references`) |
| `ZKP` | [circom](https://github.com/iden3/circom) + [snarkjs](https://github.com/iden3/snarkjs), [Halo2](https://github.com/zcash/halo2), [arkworks](https://github.com/arkworks-rs) |
| `SYN` | [SDV](https://github.com/sdv-dev/SDV), [Synthcity](https://github.com/vanderschaarlab/synthcity), [private-pgm](https://github.com/ryan112358/private-pgm) (DP-coupled, relevant to `P-08`) |
| `SDC` | [sdcMicro](https://cran.r-project.org/package=sdcMicro), [sdcTable](https://cran.r-project.org/package=sdcTable), [τ-ARGUS](https://research.cbs.nl/casc/tau.htm) — all three already cited on the `SDC` primitive and `P-09` |
| `TEE` | [AWS Nitro Enclaves](https://aws.amazon.com/ec2/nitro/nitro-enclaves/) (already in use in stepwise-privacy-cards' `flta_eval/tee/`), [Azure Confidential Computing](https://azure.microsoft.com/en-us/solutions/confidential-compute), [Open Enclave SDK](https://github.com/openenclave/openenclave) |
| `TRE` | Not really a library question — this is institutional (ONS SRS, NHS SDEs, ADR UK). [Five Safes](https://fivesafes.org/) is the governing framework, not a tool. |

---

## Contributing to this page

Open a PR with the addition, correction, or removal, and a one-line reason (a link to docs, a deployment reference, or just "this one's dead / superseded by X" is enough — the bar here is much lower than [CONTRIBUTING.md](CONTRIBUTING.md)'s bar for a card's `tooling_candidates`). No need to pin a version; if a version genuinely matters for a specific claim, say so inline rather than in a table cell that will go stale.
