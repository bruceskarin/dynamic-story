# Energy v0.1 seed data

Pulled 2026-10-12 (core) and 2026-10-13 (reserves, CO2 coefficients, Form 860) from the public sources in `../docs/data-availability-energy.md`. Rebuild with `python3 build_seed.py` from this folder (needs `openpyxl`). For Form 860, unzip `raw/eia8602024.zip` so `raw/3_1_Generator_Y2024.xlsx` is present first.

- `seed_atb_clean_costs.csv`: NREL ATB 2025 v1 (released 2026-08-27), Without Tax Credits, 2023 dollars, years 2023-2060, Conservative / Moderate / Advanced. CAPEX ($/kW) for utility PV, land-based wind, and 4-hour utility battery; LCOE ($/MWh) for PV and wind. Resource classes (PV Class 5, wind Class 4) are a proposed mid-resource pick, not an ATB designation. Feeds the R1 learning loop.
- `seed_mer_annual.csv`: EIA Monthly Energy Review annual rows 2010-2025: production by source (T1.2), consumption by source (T1.3), crude prices (T9.1), natural gas prices (T9.10). Seeds the B1 cheap-fuel loop and the clean-capacity stock.
- `seed_climate_gap.csv`: Global Carbon Budget 2024 remaining budgets and 2024 fossil CO2. Seeds the cumulative-emissions gap.
- `seed_reserves.csv`: EIA Form EIA-23L proved reserves 2014-2024 (crude oil and lease condensate; wet natural gas) plus 2024 extensions and discoveries. Seeds the fossil-reserves stock and extraction flow.
- `seed_co2_coefficients.csv`: EIA Carbon Dioxide Emissions Coefficients by Fuel (2022 factors, released 2024-09-18), lb and kg per MMBtu and per physical unit. Seeds accounting-rate fuel charges.
- `seed_capacity_860.csv`: EIA Form EIA-860 2024 nameplate MW by technology for operable units, proposed units (by Effective Year), and retirements since 2010. Seeds clean-capacity stock, builds, and retirements.
- `seed_cost_of_capital.csv`: cost-of-capital proxy for the economy-to-energy coupling (built by `build_cost_of_capital.py`). Three bands: `atb_aeo` is the NREL ATB 2025 AEO-based financing path 2023-2060 (Without Tax Credits; nominal WACC about 7.2%, real about 4.6%), `atb_reeds` is ATB's fixed ReEDS assumptions (nominal WACC 8.08%, real 5.44%) as a higher-rate band, and `market` is FRED history 2010-2025 for the Moody's Baa corporate yield and the 10-year Treasury (annual averages). Values are fractions per year.
- `raw/`: untouched downloads (FRED files added 2026-10-13 in `raw/fred_baa_dgs10/`).

### Raw files not in git

Two Form EIA-860 files are over 10 MB and are left out of the repo (they are in `.gitignore`). Download them before running the Form 860 part of `build_seed.py`:

- `raw/eia8602024.zip` (about 22 MB): EIA Form 860 2024 final data, https://www.eia.gov/electricity/data/eia860/
- `raw/3_1_Generator_Y2024.xlsx` (about 11 MB): unzip it from `eia8602024.zip`.

The seed CSVs built from them (`seed_capacity_860.csv`) are committed, so the energy model runs without them.

Still open: nothing blocking the energy v0.1 build. The cost-of-capital proxy is a placeholder band until the economy sector supplies it endogenously.
