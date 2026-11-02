# Evaluation policy

The primary score compares normalized leaf fields with the original supplied accounting ground truth. Numeric strings use exact Decimal comparison; whitespace and terminal punctuation are normalized for text. Lists are compared in order and their length is scored. Source PDF filenames anchor row alignment so an incorrectly extracted invoice ID is still scored. Duplicate source rows are rejected. A secondary printed-value score substitutes only rendered_subtotal and rendered_total. Ground truth is never passed to extraction.

Correction to the prior evaluator: missing values are no longer treated as equal to false booleans, and an unexpected object is not treated as a correct null field. The unchanged baseline extraction therefore scores 1,496 / 2,346 (63.8%), rather than the earlier permissive 1,509 / 2,346 (64.3%). Its printed-value score is 64.2%. The old figure is not a model deterioration; the scoring rules were corrected.

These are in-sample assignment results. Refined source rules were developed after inspecting source layouts and baseline error categories, with no held-out evaluation. LLM JSON parse failures remain recorded and produce missing fields, not ground-truth replacements.
