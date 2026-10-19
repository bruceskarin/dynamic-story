"""Build seed_cost_of_capital.csv: the economy-to-energy cost-of-capital proxy.

Sources (all in raw/):
- atb2025.xlsx, sheet "WACC Calc": NREL ATB 2025 v1 financial assumptions.
  AEO-based block (Without Tax Credits case, rows 2-25) and the fixed ReEDS block (rows 27-51).
- fred_baa_dgs10/: FRED Moody's Seasoned Baa corporate yield (BAA, annual) and
  10-year Treasury constant maturity (DGS10, daily, averaged here by calendar year).
Rebuild: python3 build_cost_of_capital.py (needs openpyxl).
"""
import csv, openpyxl
from collections import defaultdict

out = []
wb = openpyxl.load_workbook('raw/atb2025.xlsx', read_only=True, data_only=True)
rows = list(wb['WACC Calc'].iter_rows(max_row=52, values_only=True))
years = [v for v in rows[1] if isinstance(v, int)]
start = list(rows[1]).index(years[0])

def label(r):
    for v in r[:5]:
        if isinstance(v, str) and v not in ('AEO', 'ReEDs'):
            return v
    return None

# AEO-based block, Moderate series (Advanced/Conservative are identical in ATB 2025 financials)
want = {
    'Inflation Rate': 'inflation',
    'Interest Rate Nominal - Moderate': 'debt_rate_nominal',
    'Rate of Return on Equity Nominal - Moderate': 'equity_return_nominal',
    'Debt Fraction - Moderate': 'debt_fraction',
    'Tax Rate (Federal and State)': 'tax_rate',
    'WACC Nominal - Moderate': 'wacc_nominal',
    'WACC Real - Moderate': 'wacc_real',
}
for r in rows[2:26]:
    k = label(r)
    if k in want:
        for y, v in zip(years, r[start:start + len(years)]):
            out.append(['NREL ATB 2025 WACC Calc (AEO-based, Without Tax Credits, Moderate)', 'atb_aeo', want[k], y, round(v, 6)])
# ReEDS fixed block: first row of each label is the value (repeat rows are per scenario)
reeds = {'Interest Rate - Nominal': 'debt_rate_nominal', 'Rate of Return on Equity - Nominal': 'equity_return_nominal',
         'Debt Fraction': 'debt_fraction', 'Tax Rate (Federal and State)': 'tax_rate',
         'WACC - Nominal': 'wacc_nominal', 'WACC - Real': 'wacc_real'}
for r in rows[27:52]:
    k = label(r)
    if k in reeds:
        for y, v in zip(years, r[start:start + len(years)]):
            out.append(['NREL ATB 2025 WACC Calc (ReEDS fixed assumptions)', 'atb_reeds', reeds[k], y, round(v, 6)])

# FRED market history
with open('raw/fred_baa_dgs10/annual.csv') as f:
    for row in csv.DictReader(f):
        y = int(row['observation_date'][:4])
        if 2010 <= y <= 2025 and row['BAA']:
            out.append(["FRED BAA (Moody's Seasoned Baa corporate yield, annual avg)", 'market', 'baa_yield_nominal', y, round(float(row['BAA']) / 100, 6)])
acc = defaultdict(list)
with open('raw/fred_baa_dgs10/daily.csv') as f:
    for row in csv.DictReader(f):
        if row.get('DGS10'):
            acc[int(row['observation_date'][:4])].append(float(row['DGS10']))
for y in range(2010, 2026):
    if acc[y]:
        out.append(['FRED DGS10 (10-year Treasury, daily averaged by year)', 'market', 'treasury10_yield_nominal', y, round(sum(acc[y]) / len(acc[y]) / 100, 6)])

with open('seed_cost_of_capital.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['source', 'band', 'variable', 'year', 'value_fraction'])
    w.writerows(out)
print(len(out), 'rows')
