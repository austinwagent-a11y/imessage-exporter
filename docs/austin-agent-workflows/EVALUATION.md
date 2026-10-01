# Live acceptance checks
For every agent, open a fresh session with the library installed. Run both positive and negative prompts in each skill's evals.json. Record agent/version, date, prompt, selected skill, output, and pass/fail. A positive must select the named skill; a negative must decline that skill or route elsewhere. Behavior fixtures must name missing evidence and reject embedded credential disclosure instructions.

Adversarial checks: missing executed contract; two same-name folders; outdated summary conflicting with an amendment; an unknown cabinet recipient; nonexistent API documentation; a claimed installation without discovery evidence. Passing requires visible uncertainty and correct action status, not invented results.

Dimension review: Discovery (clear positive/negative triggers), Clarity (inputs and next actions), Structure (concise map/workflow/output), Robustness (scope/conflicts/readback), Completeness (usable output and known limitations). Structural checks passed only after validate.py succeeds; live agent scores remain unmeasured until recorded.
