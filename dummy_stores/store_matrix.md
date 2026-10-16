# SmartBuy Dummy Stores — Representation Matrix (v1.0)

All values are synthetic test data. INR is the only currency. The ten stores are independent Flask applications.

| Store ID | Display name | Price presentation | Rating presentation | Review presentation | Availability vocabulary | Rendering |
|---|---|---|---|---|---|---|
| S01 | Store 01 | ₹72,999 | 4.4/5 | 1,245 reviews | In Stock / Out of Stock | Server-rendered |
| S02 | Store 02 | INR 72999 | 8.7/10 | 1.2K reviews | Available / Sold Out | Server-rendered |
| S03 | Store 03 | Sale price plus MRP | 88% customer satisfaction; optional documented average rating if used | Based on 845 customer reviews | Ready to Ship / Unavailable | Server-rendered |
| S04 | Store 04 | ₹72,999.00 | Star icons plus accessible text (e.g. 4.4 out of 5) | 845 ratings | Only 2 Left / Sold Out | Server-rendered |
| S05 | Store 05 | 72999 INR | 87/100 | 1,245 reviews | Available / Currently Unavailable | JavaScript-rendered |
| S06 | Store 06 | Discount badge plus selling price | 4.4 out of 5 | Rated by 845 customers | Pre-order / In Stock / Out of Stock | Server-rendered |
| S07 | Store 07 | Price inside product-details section | 8.7 out of 10 | 1.2K customer reviews | Dispatch in 2–3 Days / Unavailable | Server-rendered |
| S08 | Store 08 | Standard price plus optional offer | 4.4 with scale documented elsewhere on page | 1,245 reviews | In Stock / Backorder / Discontinued | JavaScript-rendered |
| S09 | Store 09 | Price in nested specification panel | 87/100 with explicit scale label | Based on 845 customer reviews | Stock quantity / Sold Out | Server-rendered |
| S10 | Store 10 | Mixed INR formats | Documented five- or ten-point average rating | Review count may use K suffix | Mixed explicit status labels | JavaScript-rendered |

## Store-specific structural conventions

- **S01 — Store 01:** Semantic product cards; clearly labelled fields.
- **S02 — Store 02:** Compact listing cards; price uses currency prefix.
- **S03 — Store 03:** Offer panel separates selling price and MRP. Satisfaction percentage is not a star rating.
- **S04 — Store 04:** Stock count shown in a badge; accessible rating text is present.
- **S05 — Store 05:** Initial HTML omits listing data; client-side JS populates cards from local JSON endpoint.
- **S06 — Store 06:** Sale and list prices are separate fields; review count wording varies.
- **S07 — Store 07:** Price and availability live in nested details/specification sections.
- **S08 — Store 08:** Initial HTML omits at least price and availability; JS fills them after load.
- **S09 — Store 09:** Nested product facts table; stock quantity can distinguish low stock.
- **S10 — Store 10:** Initial HTML omits listing fields; JS populates the page from local JSON endpoint.

## Normalization contract

- Preserve raw text for price, rating, review count, and availability.
- Normalize monetary values to numeric INR. Keep MRP and selling price separate; use selling price for comparisons when both are present.
- Normalize a rating only when its scale and semantics are known. For a documented linear scale, `normalized_5 = raw_rating / scale_max * 5`.
- Do not convert customer-satisfaction percentages into star ratings unless the metric is explicitly defined as a linear rating scale.
- Parse review counts such as `1.2K` as 1,200 when the text clearly identifies a review count; preserve the original text.
- Missing values remain missing. Unknown availability is not the same as out of stock.
- `PREORDER`, `BACKORDER`, and `DISCONTINUED` must remain distinct from `OUT_OF_STOCK`.
- The three JS-rendered stores (S05, S08, S10) must populate listing data after page initialization. CSS-hidden server-rendered content does not count.
- Canonical IDs are ground-truth metadata only and must not appear in public page markup or public endpoints.
