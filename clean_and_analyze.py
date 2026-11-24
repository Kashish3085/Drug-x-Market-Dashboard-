"""Clean the raw claims, load all tables into SQLite and run sql/analysis.sql.

Outputs:
  data/claims_clean.csv   dashboard-ready table (open this in Tableau / Power BI)
  data/access.db          SQLite database with all four tables
  docs/analysis_results.md  every SQL result as a table
"""
import sqlite3
import pandas as pd

raw = pd.read_csv("data/raw_claims.csv", parse_dates=["fill_date"])
log = [f"Raw rows: {len(raw)}"]

# 1. Duplicates
df = raw.drop_duplicates()
log.append(f"Removed {len(raw) - len(df)} exact duplicate claims")

# 2. Inconsistent state codes (e.g. 'ca ' -> 'CA')
bad = (df.state != df.state.str.strip().str.upper()).sum()
df["state"] = df.state.str.strip().str.upper()
log.append(f"Fixed {bad} badly formatted state codes")

# 3. Missing copay: without a copay card, copay equals what the patient paid, so it can be recovered.
#    With a copay card the original copay is unknown, so it stays blank (flagged, not guessed).
miss = df.copay_usd.isna()
fixable = miss & ~df.copay_card_used
df.loc[fixable, "copay_usd"] = df.loc[fixable, "oop_after_card_usd"]
log.append(f"Missing copay values: {miss.sum()}; recovered {fixable.sum()} (no copay card), left {miss.sum() - fixable.sum()} blank")

# 4. Business rule checks
assert df.claim_id.is_unique, "claim_id must be unique after cleaning"
assert not (df.filled & (df.claim_status == "Rejected")).any(), "a rejected claim cannot be filled"
assert not (df.abandoned & (df.claim_status == "Rejected")).any(), "only paid claims can be abandoned"
log.append("Business rule checks passed (unique claim IDs, rejected claims never filled or abandoned)")

df["quarter"] = df.fill_date.dt.year.astype(str) + "-Q" + df.fill_date.dt.quarter.astype(str)
df["month"] = df.fill_date.dt.to_period("M").astype(str)

payers = pd.read_csv("data/payers.csv")
formulary = pd.read_csv("data/formulary.csv")
regions = pd.read_csv("data/regions.csv")

# Flat table for the dashboard (one row per claim, everything joined)
flat = (df.merge(payers, on="payer_id")
          .merge(formulary, on=["payer_id", "quarter"])
          .merge(regions, on="state"))
flat.to_csv("data/claims_clean.csv", index=False)
log.append(f"Clean rows: {len(flat)}")

con = sqlite3.connect("data/access.db")
for name, t in [("claims", df), ("payers", payers), ("formulary", formulary), ("regions", regions)]:
    t.to_sql(name, con, if_exists="replace", index=False)

out = ["# Analysis results", "", "## Data cleaning log", ""] + [f"- {l}" for l in log] + [""]
for block in open("sql/analysis.sql").read().split("-- name: ")[1:]:
    name, sql = block.split("\n", 1)
    res = pd.read_sql(sql, con)
    out += [f"## {name.strip()}", "", res.to_markdown(index=False), ""]
    print(f"\n== {name.strip()}\n{res.to_string(index=False)}")
open("docs/analysis_results.md", "w").write("\n".join(out))
print("\n".join(log))
