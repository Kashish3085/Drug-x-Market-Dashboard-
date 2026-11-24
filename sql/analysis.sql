-- name: kpis
SELECT COUNT(*)                                        AS total_claims,
       ROUND(100.0 * AVG(claim_status = 'Rejected'), 1) AS reject_rate_pct,
       ROUND(100.0 * SUM(abandoned) / SUM(claim_status = 'Paid'), 1) AS abandon_rate_pct,
       ROUND(100.0 * AVG(filled), 1)                    AS fill_rate_pct,
       ROUND(AVG(CASE WHEN claim_status = 'Paid' THEN oop_after_card_usd END), 2) AS avg_patient_oop_usd
FROM claims;

-- name: by_channel
SELECT p.channel,
       COUNT(*) AS claims,
       ROUND(100.0 * AVG(c.claim_status = 'Rejected'), 1) AS reject_rate_pct,
       ROUND(100.0 * SUM(c.abandoned) / SUM(c.claim_status = 'Paid'), 1) AS abandon_rate_pct,
       ROUND(AVG(CASE WHEN c.claim_status = 'Paid' THEN c.oop_after_card_usd END), 2) AS avg_oop_usd
FROM claims c JOIN payers p ON c.payer_id = p.payer_id
GROUP BY p.channel ORDER BY claims DESC;

-- name: reject_reasons
SELECT reject_reason, COUNT(*) AS rejected_claims,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM claims WHERE claim_status = 'Rejected'), 1) AS share_pct
FROM claims WHERE claim_status = 'Rejected'
GROUP BY reject_reason ORDER BY rejected_claims DESC;

-- name: access_restrictions
SELECT f.formulary_tier, f.prior_auth, f.step_therapy,
       COUNT(*) AS claims,
       ROUND(100.0 * AVG(c.claim_status = 'Rejected'), 1) AS reject_rate_pct
FROM claims c JOIN formulary f ON c.payer_id = f.payer_id AND c.quarter = f.quarter
GROUP BY 1, 2, 3 ORDER BY reject_rate_pct DESC;

-- name: oop_vs_abandonment
SELECT CASE WHEN oop_after_card_usd <= 10 THEN '1) $0-10'
            WHEN oop_after_card_usd <= 50 THEN '2) $10-50'
            WHEN oop_after_card_usd <= 100 THEN '3) $50-100'
            ELSE '4) $100+' END AS oop_band,
       COUNT(*) AS paid_claims,
       ROUND(100.0 * AVG(abandoned), 1) AS abandon_rate_pct
FROM claims WHERE claim_status = 'Paid'
GROUP BY 1 ORDER BY 1;

-- name: copay_card_effect
SELECT copay_card_used, COUNT(*) AS paid_claims,
       ROUND(AVG(oop_after_card_usd), 2) AS avg_oop_usd,
       ROUND(100.0 * AVG(abandoned), 1) AS abandon_rate_pct
FROM claims c JOIN payers p ON c.payer_id = p.payer_id
WHERE claim_status = 'Paid' AND p.channel = 'Commercial'
GROUP BY 1;

-- name: payer_quarter_trend
SELECT p.payer_name, c.quarter,
       ROUND(100.0 * AVG(c.claim_status = 'Rejected'), 1) AS reject_rate_pct,
       ROUND(100.0 * AVG(c.filled), 1) AS fill_rate_pct
FROM claims c JOIN payers p ON c.payer_id = p.payer_id
WHERE p.payer_name IN ('Payer B', 'Payer E', 'Payer G')
GROUP BY 1, 2 ORDER BY 1, 2;

-- name: by_region
SELECT r.region, COUNT(*) AS claims,
       ROUND(100.0 * AVG(c.filled), 1) AS fill_rate_pct
FROM claims c JOIN regions r ON c.state = r.state
GROUP BY 1 ORDER BY claims DESC;
