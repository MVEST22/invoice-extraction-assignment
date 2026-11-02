# Assignment 3 - verified interim results

The rule-based method and Gemini 3.5 Flash-Lite have each processed all 50 invoices, achieving 63.8% and 81.7% field accuracy against the supplied accounting ground truth respectively. The main errors concern VAT, line-item prices and amounts, discounts, and address/description formatting. Some invoices intentionally print amounts that differ from the accounting answers; using the supplied printed subtotal/total instead gives 64.2% and 82.4%. Neither completed method produced an entirely exact invoice. Gemini 3.8 Flash has processed only five invoices because of connection/server failures, so a full-sample accuracy comparison is not yet justified; its missing 45 invoices must not be interpreted as ordinary model extraction mistakes. The refined method's code is prepared but it has not yet run. Completed results are genuine saved outputs, with no missing predictions replaced from ground truth.

| Method | Coverage | Field accuracy | Main issue/status |
|---|---:|---:|---|
| 1: non-LLM rules | 50/50 | 63.8% | VAT, line items, discounts and addresses |
| 2: Gemini 3.5 Flash-Lite | 50/50 | 81.7% | VAT, line-item prices/amounts and discounts |
| 3: Gemini 3.8 Flash | 5/50 | Pending full run | Service/network failures; sample incomplete |
| 4: refined hybrid | 0/50 | Not yet run | Code prepared; execution pending |

For the user-selected Free Tier project with billing disabled, the eligible API usage has a $0 charge and no paid credits were purchased; billing status is not independently verified by the inference API. Flash-Lite has 24,892 recorded input and 32,499 output tokens over ten successful requests; Flash has 2,614 input and 2,997 output tokens in its one saved successful request. Failed-request usage is not available. Flash is the higher-standard-price model: published input/output rates checked on 2 November 2026 were $0.30/$2.50 per million tokens for 3.5 Flash-Lite and $0.75/$3.75 for 3.8 Flash under the then-current standard rates, separately from free allowances. Free request/token limits and service availability can interrupt completion. The planned refinement reuses existing predictions with no further LLM calls.
