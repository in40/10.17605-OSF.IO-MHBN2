# REAL TODO STEPS

Next concrete steps toward the registered pilot. Order = dependency order.

1. **Settle ethics review body.** Solo/self-funded: cannot self-review. Options: independent ethics review service (независимая комиссия по этике / independent IRB-equivalent) or affiliate with a university whose local committee reviews the protocol. Toloka platform review is ToS moderation, NOT IRB-equivalent — does not satisfy the registration requirement. Record committee name, approval number, approval date in frozen config + OSF metadata before any human ratings.
2. **Smoke test (prep + pass).** 10 texts; data excluded from calibration and confirmatory decisions. Includes:
   - API verification: access + quota for Qwen 3.8 Max (judge), Qwen3.7 Plus, DeepSeek-V4, Yandex Alisa, Sber GigaChat; terms check (no-training opt-out, retention); pinned checkpoint IDs.
   - Prompt iteration: item-gen + judge prompts, rubrics, JSON schemas (Russian) — iterate freely here.
   - Pipeline: hashing, storage, parsing/retry/missing logic, refusal handling.
   - **Exit criterion: freeze prompts/rubrics/schemas/checkpoints (hash + OSF upload) before pilot starts.**
3. **Pilot.** 45–60 texts (15–20 per confirmatory genre). Machine-only calibration goals can start before ethics approval; human-rating goals (instructions/timing, Fleiss κ, ICC) wait for step 1.
4. **Pilot freeze.** Signed decision log: δ_d, k_d, b_d, deviations, code hash → frozen configuration file.
