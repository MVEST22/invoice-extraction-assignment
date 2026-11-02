# Assignment 3 - run pending

The non-LLM baseline processed all 50 invoices and matched 1,496 of 2,346 ground-truth fields (63.8%), with no fully exact invoices. Its main errors concern VAT rates, line-item amounts, wrapped descriptions, discounts and addresses. The two real LLM runs and the refined comparison are still pending; the completed notebook will regenerate this report from actual outputs, including a separate printed-value score for deliberately inconsistent invoice totals.

| Method | Status | Verified field score |
|---|---|---:|
| Non-LLM rules | Completed on 50 invoices | 63.8% |
| Qwen 1.5B | Not yet run | Pending |
| Qwen 7B (4-bit) | Not yet run | Pending |
| Refined hybrid | Not yet run | Pending |

No paid API calls have been made. The planned open-model Colab runs have no API fee; token counts and generation times will be recorded when executed. A larger open model is not a purchased API tier: interpreting it as the “more expensive LLM” is a disclosed higher-compute substitution, subject to the lecturer's interpretation. Free GPU availability and session time are limited. The refined method reuses existing predictions without another LLM call.
