"""Generate a simulated pharmacy claims dataset for one branded drug ("Drug X").

The data is simulated, but the patterns follow how US market access works:
prior authorization and step therapy cause rejections, high copays cause
patients to abandon prescriptions, and copay cards reduce abandonment.
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
N = 40000

# ---------- Payers ----------
payers = pd.DataFrame({
    "payer_id": [f"P{i:02d}" for i in range(1, 13)],
    "payer_name": [f"Payer {c}" for c in "ABCDEFGHIJKL"],
    "channel": ["Commercial"] * 6 + ["Medicare Part D"] * 4 + ["Medicaid"] * 2,
    "covered_lives_m": [12.5, 9.8, 7.1, 4.4, 3.0, 1.6, 6.2, 4.9, 2.7, 1.3, 5.5, 3.8],
})

# ---------- Formulary by quarter ----------
quarters = ["2025-Q1", "2025-Q2", "2025-Q3", "2025-Q4"]
tier_choices = ["Tier 2 (Preferred)", "Tier 3 (Non-preferred)", "Tier 4 (Specialty)", "Not Covered"]
rows = []
for _, p in payers.iterrows():
    tier = rng.choice(tier_choices, p=[0.35, 0.35, 0.2, 0.1])
    pa = rng.random() < 0.5
    st = rng.random() < 0.3
    for q in quarters:
        # Two payers improve access mid-year (a "contract win"), one gets worse
        if p.payer_id in ("P02", "P07") and q >= "2025-Q3":
            tier, pa, st = "Tier 2 (Preferred)", False, False
        if p.payer_id == "P05" and q >= "2025-Q3":
            tier, pa = "Not Covered", True
        rows.append([p.payer_id, q, tier, pa, st])
formulary = pd.DataFrame(rows, columns=["payer_id", "quarter", "formulary_tier", "prior_auth", "step_therapy"])

# ---------- Claims ----------
states = {"CA": "West", "WA": "West", "AZ": "West", "TX": "South", "FL": "South", "GA": "South",
          "NY": "Northeast", "PA": "Northeast", "MA": "Northeast", "IL": "Midwest", "OH": "Midwest", "MI": "Midwest"}
state_w = np.array([12, 3, 3, 10, 8, 4, 7, 5, 3, 5, 4, 3], float)

dates = pd.to_datetime("2025-01-01") + pd.to_timedelta(rng.integers(0, 365, N), unit="D")
claims = pd.DataFrame({
    "claim_id": [f"C{i:06d}" for i in range(1, N + 1)],
    "fill_date": dates,
    "patient_id": [f"PT{x:05d}" for x in rng.integers(1, 15000, N)],
    "payer_id": rng.choice(payers.payer_id, N, p=payers.covered_lives_m / payers.covered_lives_m.sum()),
    "state": rng.choice(list(states), N, p=state_w / state_w.sum()),
    "new_to_brand": rng.random(N) < 0.35,
})
claims["quarter"] = claims.fill_date.dt.year.astype(str) + "-Q" + claims.fill_date.dt.quarter.astype(str)
claims = claims.merge(formulary, on=["payer_id", "quarter"]).merge(payers[["payer_id", "channel"]], on="payer_id")

# Rejection logic
p_reject = np.full(len(claims), 0.04)
p_reject += np.where(claims.formulary_tier == "Not Covered", 0.75, 0)
p_reject += np.where(claims.prior_auth & claims.new_to_brand, 0.35, 0)
p_reject += np.where(claims.step_therapy & claims.new_to_brand, 0.15, 0)
rejected = rng.random(len(claims)) < np.clip(p_reject, 0, 0.95)

def reason(r):
    opts, w = ["Other"], [0.2]
    if r.formulary_tier == "Not Covered": opts.append("Not on formulary"); w.append(3)
    if r.prior_auth: opts.append("Prior authorization required"); w.append(2)
    if r.step_therapy: opts.append("Step therapy required"); w.append(1)
    w = np.array(w) / sum(w)
    return rng.choice(opts, p=w)
claims["claim_status"] = np.where(rejected, "Rejected", "Paid")
claims["reject_reason"] = [reason(r) if rj else "" for r, rj in zip(claims.itertuples(), rejected)]

# Copay before any copay card, by tier and channel
base = claims.formulary_tier.map({"Tier 2 (Preferred)": 35, "Tier 3 (Non-preferred)": 85,
                                  "Tier 4 (Specialty)": 160, "Not Covered": 0})
base = base * claims.channel.map({"Commercial": 1.0, "Medicare Part D": 1.3, "Medicaid": 0.05})
claims["copay_usd"] = np.where(rejected, 0, np.round(base * rng.uniform(0.7, 1.3, len(claims)), 2))

# Copay cards: commercial only (government plans cannot use them)
claims["copay_card_used"] = (~rejected) & (claims.channel == "Commercial") & (rng.random(len(claims)) < 0.45)
claims["oop_after_card_usd"] = np.where(claims.copay_card_used, np.minimum(claims.copay_usd, 10), claims.copay_usd)

# Abandonment: patient does not pick up a paid claim; rises with out-of-pocket cost
p_ab = 0.05 + 0.0018 * claims.oop_after_card_usd
claims["abandoned"] = (~rejected) & (rng.random(len(claims)) < np.clip(p_ab, 0, 0.6))
claims["filled"] = (~rejected) & (~claims.abandoned)

# A few data quality issues, so the cleaning step has something to do
dirty = claims.sample(150, random_state=1).index
claims.loc[dirty[:60], "state"] = claims.loc[dirty[:60], "state"].str.lower() + " "
claims.loc[dirty[60:110], "copay_usd"] = np.nan
dups = claims.sample(90, random_state=2)
claims = pd.concat([claims, dups])

claims = claims[["claim_id", "fill_date", "patient_id", "payer_id", "state", "new_to_brand",
                 "claim_status", "reject_reason", "copay_usd", "copay_card_used",
                 "oop_after_card_usd", "abandoned", "filled"]]
claims.to_csv("data/raw_claims.csv", index=False)
payers.to_csv("data/payers.csv", index=False)
formulary.to_csv("data/formulary.csv", index=False)
pd.DataFrame({"state": list(states), "region": list(states.values())}).to_csv("data/regions.csv", index=False)
print("raw claims:", len(claims))
