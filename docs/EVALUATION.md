# APX Evaluation

## 1. Evaluation philosophy

APX treats evaluation as a separate engineering layer. Evaluation code should observe existing system behavior rather than silently replacing validation, retrieval, decision, risk, guardrail, or action logic.

The repository's V1.1 evaluation design defines six layers:

1. extraction;
2. exception detection;
3. retrieval;
4. decision;
5. action;
6. business outcomes.

## 2. Retrieval evaluation

The retrieval evaluator is intended to measure the existing retrieval pipeline using explicit relevance judgments.

Core retrieval metrics include:

- Recall@5
- Recall@10
- MRR
- nDCG@10

The evaluation contract must keep the following concepts separate:

- retrieved candidate;
- relevant evidence;
- valid evidence;
- evidence applicable to the exception;
- evidence used by downstream decision logic.

A low retrieval score is not, by itself, evidence that a specific retriever component is defective. Ground-truth semantics and candidate boundaries must be checked first.

## 3. Ground truth

APX has historically undergone repairs to evidence relevance semantics and temporal anchoring. Those artifacts are preserved under [history](history/README.md).

The current engineering rule is:

> Relevance must be defensible from explicit evidence applicability and validity, not inferred solely from vendor ownership.

Historical resolution evidence should be evaluated against the relevant exception semantics. Generic policy, contract, and payment-term evidence should not become relevant merely because it belongs to the same vendor.

Do not construct benchmark labels from retrieval output.

## 4. Reproducibility

Benchmark inputs should be deterministic where the underlying system is deterministic.

Important controls include:

- fixed random seed;
- deterministic synthetic data;
- explicit reference date for simulated evidence validity;
- persisted evaluation artifacts;
- versioned benchmark configuration;
- tests for dataset and metric determinism.

The historical temporal fix introduced the canonical simulated reference date used by the benchmark and evidence corpus. The detailed rationale is retained in the archived temporal-fix report.

## 5. Recorded verification

The latest repository documentation records Phase 6D verification including:

- focused observability/security tests;
- tracing regression coverage;
- persistence regression coverage;
- validator regression coverage;
- evidence regression coverage;
- risk, guardrail, and action regression coverage;
- API verification.

The Phase 6D report records **180 passed and 0 failed** in its regression accounting, with the API suite separately recorded as **60 passed and 1 expected skip**.

These are recorded historical verification results, not a claim that this document has independently executed the suite in the current environment.

Run the current suite before treating those numbers as a fresh CI result:

```bash
python -m pytest apx/tests -q
```

## 6. Benchmark interpretation

Evaluation targets are targets, not achieved results.

Do not:

- tune implementation to an unverified benchmark;
- fabricate missing relevance labels;
- convert target thresholds into reported performance;
- present historical benchmark results as current production performance.

When a metric is unavailable, document why it is unavailable rather than inventing a value.
