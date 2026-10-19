"""Build the v0.1 energy seed dataset for Dynamic Story from raw public sources in ./raw."""
import csv, openpyxl
wb = openpyxl.load_workbook('raw/atb2025.xlsx', read_only=True, data_only=True)
PICK = {('UtilityPV','Class5'):'utility_pv', ('LandbasedWind','Class4'):'landbased_wind',
        ('Utility-Scale Battery Storage','4Hr Battery Storage'):'utility_battery_4h'}
out = []
for sheet, metric, unit in [('Summary_CAPEX','capex','$/kW (2023$)'), ('Summary_LCOE','lcoe','$/MWh (2023$)')]:
    rows = list(wb[sheet].iter_rows(values_only=True)); h = rows[0]
    for r in rows[1:]:
        if r[1] != 'Without Tax Credits' or (r[4], r[5]) not in PICK: continue
        for y, v in zip(h[7:], r[7:]):
            if isinstance(y, int) and v is not None:
                out.append([PICK[(r[4], r[5])], metric, r[2], y, round(v, 2), unit, f'NREL ATB 2025 v1 {sheet} {r[4]} {r[5]}'])
with open('seed_atb_clean_costs.csv','w',newline='') as f:
    w = csv.writer(f); w.writerow(['technology','metric','cost_case','year','value','unit','source']); w.writerows(out)

MER = {'MER_T01.02.csv':None,'MER_T01.03.csv':None,'MER_T09.01.csv':['Crude Oil Domestic First Purchase Price','Refiner Acquisition Cost of Crude Oil, Composite'],
       'MER_T09.10.csv':['Natural Gas Price, Wellhead','Natural Gas Price, Citygate','Natural Gas Price, Electric Power Sector','Natural Gas Price, Delivered to Consumers, Residential']}
rows_out = []
for fn, keep in MER.items():
    for r in csv.DictReader(open('raw/'+fn)):
        ym = r['YYYYMM']
        if not ym.endswith('13') or int(ym[:4]) < 2010: continue
        if keep and r['Description'] not in keep: continue
        try: v = float(r['Value'])
        except ValueError: continue
        rows_out.append([r['Description'], int(ym[:4]), v, r['Unit'], 'EIA MER ' + fn[4:-4]])
with open('seed_mer_annual.csv','w',newline='') as f:
    w = csv.writer(f); w.writerow(['series','year','value','unit','source']); w.writerows(sorted(rows_out))

with open('seed_climate_gap.csv','w',newline='') as f:
    w = csv.writer(f); w.writerow(['quantity','value','unit','as_of','source'])
    w.writerows([['remaining_co2_budget_1p5C_50pct',235,'GtCO2','start of 2025','Global Carbon Budget 2024'],
                 ['remaining_co2_budget_1p7C_50pct',585,'GtCO2','start of 2025','Global Carbon Budget 2024'],
                 ['remaining_co2_budget_2C_50pct',1110,'GtCO2','start of 2025','Global Carbon Budget 2024'],
                 ['fossil_co2_emissions',37.4,'GtCO2/yr','2024 (preliminary)','Global Carbon Budget 2024']])
print(len(out), len(rows_out))


# --- v0.1.1 additions (2026-10-13): reserves, CO2 coefficients, Form 860 capacity ---
from collections import defaultdict
from pathlib import Path
RAW = Path('raw')

rows = []
wb5 = openpyxl.load_workbook(RAW/'ARR_2024_TABLE_05.xlsx', data_only=True)
for r in wb5.active.iter_rows(values_only=True):
    if isinstance(r[0], int) and r[5] is not None:
        rows.append(['crude_oil_lease_condensate_proved_reserves', r[0], r[5], 'million barrels', 'EIA Form EIA-23L Table 5, year-end'])
        if r[4] is not None:
            rows.append(['crude_oil_lease_condensate_production', r[0], r[4], 'million barrels/yr', 'EIA Form EIA-23L Table 5 estimated production'])
wb7 = openpyxl.load_workbook(RAW/'ARR_2024_TABLE_07.xlsx', data_only=True)
for r in wb7.active.iter_rows(values_only=True):
    if isinstance(r[0], int) and r[5] is not None:
        rows.append(['natural_gas_wet_proved_reserves', r[0], r[5], 'billion cubic feet', 'EIA Form EIA-23L Table 7, year-end'])
        if r[4] is not None:
            rows.append(['natural_gas_wet_production', r[0], r[4], 'billion cubic feet/yr', 'EIA Form EIA-23L Table 7 estimated production'])
rows.append(['crude_oil_extensions_discoveries', 2024, 5145, 'million barrels', 'EIA Form EIA-23L Table 1'])
rows.append(['natural_gas_extensions_discoveries', 2024, 67764, 'billion cubic feet', 'EIA Form EIA-23L Table 1'])
with open('seed_reserves.csv','w',newline='') as f:
    w = csv.writer(f); w.writerow(['series','year','value','unit','source']); w.writerows(sorted(rows, key=lambda x:(x[0],x[1])))

co2 = []
wb = openpyxl.load_workbook(RAW/'co2_vol_mass.xlsx', data_only=True)
for r in wb.active.iter_rows(values_only=True):
    fuel = r[0]
    if not fuel or not isinstance(fuel, str) or not isinstance(r[5], (int, float)):
        continue
    fuel = fuel.strip(); unit_mass = r[2]
    co2.append([fuel, round(r[5], 2), 'lb CO2 / MMBtu', 'EIA CO2 Emissions Coefficients (2022 factors, released 2024-09-18)'])
    if isinstance(r[6], (int, float)):
        co2.append([fuel, round(r[6], 2), 'kg CO2 / MMBtu', 'EIA CO2 Emissions Coefficients (2022 factors, released 2024-09-18)'])
    if isinstance(r[1], (int, float)) and unit_mass:
        co2.append([fuel, round(r[1], 2), f'lb CO2 / {unit_mass}', 'EIA CO2 Emissions Coefficients (2022 factors, released 2024-09-18)'])
    if isinstance(r[3], (int, float)) and unit_mass:
        co2.append([fuel, round(r[3], 2), f'kg CO2 / {unit_mass}', 'EIA CO2 Emissions Coefficients (2022 factors, released 2024-09-18)'])
with open('seed_co2_coefficients.csv','w',newline='') as f:
    w = csv.writer(f); w.writerow(['fuel','value','unit','source']); w.writerows(co2)

# Expect 3_1_Generator_Y2024.xlsx already extracted from eia8602024.zip
wb_g = openpyxl.load_workbook(RAW/'3_1_Generator_Y2024.xlsx', data_only=True)
capacity_rows = []
ws = wb_g['Operable']; rows_all = list(ws.iter_rows(values_only=True))
header = [str(x).strip() if x else '' for x in rows_all[1]]
ti, ni = header.index('Technology'), header.index('Nameplate Capacity (MW)')
agg, n_units = defaultdict(float), defaultdict(int)
for r in rows_all[2:]:
    tech, mw = r[ti], r[ni]
    if tech is None or not isinstance(mw, (int, float)): continue
    agg[tech] += mw; n_units[tech] += 1
for tech, mw in sorted(agg.items(), key=lambda x: -x[1]):
    capacity_rows.append(['operable', tech, 2024, round(mw, 1), n_units[tech], 'MW nameplate', 'EIA Form EIA-860 2024 Operable'])
ws = wb_g['Proposed']; rows_all = list(ws.iter_rows(values_only=True))
header = [str(x).strip() if x else '' for x in rows_all[1]]
ti, ni, yi = header.index('Technology'), header.index('Nameplate Capacity (MW)'), header.index('Effective Year')
agg, n_units = defaultdict(float), defaultdict(int)
for r in rows_all[2:]:
    tech, mw, y = r[ti], r[ni], r[yi]
    if tech is None or not isinstance(mw, (int, float)): continue
    year = int(y) if isinstance(y, (int, float)) else 0
    agg[(tech, year)] += mw; n_units[(tech, year)] += 1
for (tech, year), mw in sorted(agg.items(), key=lambda x: (x[0][1] or 9999, -x[1])):
    capacity_rows.append(['proposed', tech, year if year else '', round(mw, 1), n_units[(tech, year)], 'MW nameplate', 'EIA Form EIA-860 2024 Proposed'])
ws = wb_g['Retired and Canceled']; rows_all = list(ws.iter_rows(values_only=True))
header = [str(x).strip() if x else '' for x in rows_all[1]]
ti = header.index('Technology'); ni = header.index('Nameplate Capacity (MW)')
ry = next(i for i,h in enumerate(header) if h.startswith('Retirement Year'))
si = header.index('Status')
agg, n_units = defaultdict(float), defaultdict(int)
for r in rows_all[2:]:
    if r[si] and 'Cancel' in str(r[si]): continue
    tech, mw, y = r[ti], r[ni], r[ry]
    if tech is None or not isinstance(mw, (int, float)): continue
    if not isinstance(y, (int, float)) or y < 2010: continue
    agg[(tech, int(y))] += mw; n_units[(tech, int(y))] += 1
for (tech, year), mw in sorted(agg.items(), key=lambda x: (x[0][1], -x[1])):
    capacity_rows.append(['retired', tech, year, round(mw, 1), n_units[(tech, year)], 'MW nameplate', 'EIA Form EIA-860 2024 Retired (Retirement Year >= 2010)'])
with open('seed_capacity_860.csv','w',newline='') as f:
    w = csv.writer(f); w.writerow(['status','technology','year','nameplate_mw','unit_count','unit','source']); w.writerows(capacity_rows)
print('reserves', len(rows), 'co2', len(co2), 'capacity', len(capacity_rows))
