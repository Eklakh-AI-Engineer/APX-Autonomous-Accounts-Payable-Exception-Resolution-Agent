# Master scoreboard

**Status: historical failed run; not current verification.** Source: `apx/evaluation/results/benchmark_dev_20260819_171101.json`, timestamp 2026-08-19, DEV, seed 42, reference date 2026-08-29, 500 invoices.

| Layer / measure | Recorded result | Gate / interpretation |
|---|---:|---|
| Extraction F1 | 1.000 | Synthetic structured-input measure; not OCR extraction evidence |
| Detection precision | 0.1541 | Weak precision |
| Detection recall | 0.9688 | High recall with many false positives |
| Detection F1 | 0.2659 | Fails recorded 0.85 target |
| Retrieval Recall@5 | 0.60 | Fails recorded 0.70 target |
| Retrieval MRR / nDCG@10 | 0.55 / 0.60 | Historical only |
| Valid evidence rate | 0.03 | Material evidence quality gap |
| Vendor scope correctness | 0.09 | Material grounding gap |
| Business decision accuracy | 0.274 | Historical result |
| Automation rate | 0.024 | Fails recorded 0.50 target |
| Unauthorized action rate | 0.00 | Simulated benchmark field only; not proof of API/execution authorization |
| Estimated cost | $514 total; $1.028/case | Historical estimate, model assumptions not independently checked |
| Mean latency | 2712.5 ms | Historical result |

The artifact says `passed: false` and lists detection F1, retrieval Recall@5 and automation-rate gate failures. No before/after comparison is available because no current benchmark could run in this environment. See `benchmark_manifest.json` for dataset and corpus hashes and reproduction command.
