# Analysis results

## Data cleaning log

- Raw rows: 40090
- Removed 90 exact duplicate claims
- Fixed 60 badly formatted state codes
- Missing copay values: 50; recovered 39 (no copay card), left 11 blank
- Business rule checks passed (unique claim IDs, rejected claims never filled or abandoned)
- Clean rows: 40000

## kpis

|   total_claims |   reject_rate_pct |   abandon_rate_pct |   fill_rate_pct |   avg_patient_oop_usd |
|---------------:|------------------:|-------------------:|----------------:|----------------------:|
|          40000 |              12.7 |               18.2 |            71.4 |                 73.44 |

## by_channel

| channel         |   claims |   reject_rate_pct |   abandon_rate_pct |   avg_oop_usd |
|:----------------|---------:|------------------:|-------------------:|--------------:|
| Commercial      |    24395 |              15.2 |               17.3 |         66.98 |
| Medicare Part D |     9683 |               7.2 |               27.4 |        127.38 |
| Medicaid        |     5922 |              11.2 |                6.2 |          6.68 |

## reject_reasons

| reject_reason                |   rejected_claims |   share_pct |
|:-----------------------------|------------------:|------------:|
| Prior authorization required |              3119 |        61.5 |
| Other                        |               913 |        18   |
| Step therapy required        |               571 |        11.3 |
| Not on formulary             |               468 |         9.2 |

## access_restrictions

| formulary_tier         |   prior_auth |   step_therapy |   claims |   reject_rate_pct |
|:-----------------------|-------------:|---------------:|---------:|------------------:|
| Not Covered            |            1 |              0 |      967 |              85.2 |
| Tier 3 (Non-preferred) |            1 |              1 |     2419 |              22.2 |
| Tier 2 (Preferred)     |            1 |              0 |      798 |              16.5 |
| Tier 4 (Specialty)     |            1 |              0 |     9601 |              16.5 |
| Tier 3 (Non-preferred) |            1 |              0 |     5886 |              16.3 |
| Tier 2 (Preferred)     |            0 |              1 |     1046 |               9.5 |
| Tier 4 (Specialty)     |            0 |              1 |     4575 |               8.3 |
| Tier 3 (Non-preferred) |            0 |              0 |     4101 |               3.9 |
| Tier 2 (Preferred)     |            0 |              0 |     5148 |               3.8 |
| Tier 4 (Specialty)     |            0 |              0 |     5459 |               3.6 |

## oop_vs_abandonment

| oop_band   |   paid_claims |   abandon_rate_pct |
|:-----------|--------------:|-------------------:|
| 1) $0-10   |         14438 |                6.5 |
| 2) $10-50  |          4159 |               11.9 |
| 3) $50-100 |          4464 |               19.7 |
| 4) $100+   |         11868 |               34.2 |

## copay_card_effect

|   copay_card_used |   paid_claims |   avg_oop_usd |   abandon_rate_pct |
|------------------:|--------------:|--------------:|-------------------:|
|                 0 |         11296 |        114.36 |               26.2 |
|                 1 |          9382 |          9.94 |                6.6 |

## payer_quarter_trend

| payer_name   | quarter   |   reject_rate_pct |   fill_rate_pct |
|:-------------|:----------|------------------:|----------------:|
| Payer B      | 2025-Q1   |              17.3 |            69.9 |
| Payer B      | 2025-Q2   |              16.9 |            71   |
| Payer B      | 2025-Q3   |               4.2 |            86.7 |
| Payer B      | 2025-Q4   |               3.8 |            86.9 |
| Payer E      | 2025-Q1   |               3.5 |            80.7 |
| Payer E      | 2025-Q2   |               5   |            82.8 |
| Payer E      | 2025-Q3   |              83.6 |            16.2 |
| Payer E      | 2025-Q4   |              87   |            11.9 |
| Payer G      | 2025-Q1   |               4.3 |            54.7 |
| Payer G      | 2025-Q2   |               3   |            54.8 |
| Payer G      | 2025-Q3   |               3.8 |            83.9 |
| Payer G      | 2025-Q4   |               3.4 |            84.3 |

## by_region

| region    |   claims |   fill_rate_pct |
|:----------|---------:|----------------:|
| South     |    13191 |            71.6 |
| West      |    10772 |            71.4 |
| Northeast |     8877 |            70.9 |
| Midwest   |     7160 |            71.6 |
