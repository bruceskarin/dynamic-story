# Data availability: Energy (and Climate feed)

**Dynamic Story** · checked 2026-10-12 · supports Simulation Spec §2 and §19

Status: the public sources named for the first simulation are live and downloadable. No paywall blocked the core series below.

## Climate → Energy (cumulative emissions gap)

| Need | Source | Live status (2026-10-12) |
|---|---|---|
| Remaining CO2 budget by warming level | Global Carbon Budget 2024 (Friedlingstein et al.; GCP) | Confirmed: ~235 GtCO2 from beginning of 2025 for 50% likelihood of 1.5°C; ~585 GtCO2 for 1.7°C; ~1110 GtCO2 for 2°C |
| Fossil CO2 emissions | Same | Confirmed: ~37.4 GtCO2 in 2024 (preliminary) |
| Atmospheric CO2 | NOAA GML (Mauna Loa / global) | Named in spec; not re-fetched this pass |
| US sector emissions | EPA GHG Inventory | Named in spec; not re-fetched this pass |

Do not use the chat's "400 billion tons over" example. The live quantity is the remaining budget.

## Energy stocks, flows, and prices

| Need | Source | Live status (2026-10-12) |
|---|---|---|
| Production, consumption, stocks, trade, prices | EIA Monthly Energy Review | Live: August 2026 release at https://www.eia.gov/totalenergy/data/monthly/ (PDF, XLS, CSV). Tables E1–E4 cover primary energy overview, production, consumption, and renewables |
| Near-term price and production bands | EIA Short-Term Energy Outlook / Winter Fuels Outlook | Live press release 2026-10-06 with 2025–2027 markers (e.g. Brent, Henry Hub, US crude production) |
| Long-range scenario bands | EIA Annual Energy Outlook | Named in spec; use for high/middle/low paths, not point forecasts |
| Proved reserves (US) | EIA Crude Oil and Natural Gas Proved Reserves | Named in spec |
| World reserves / production context | Energy Institute Statistical Review | Named in spec |
| Capacity, builds, retirements | EIA Form 860 / Electric Power Annual | Named in spec |
| CO2 per unit of fuel | EIA carbon dioxide emission coefficients | Named in spec |

## Clean capacity costs and learning (R1 loop)

| Need | Source | Live status (2026-10-12) |
|---|---|---|
| CAPEX, OPEX, performance, learning scenarios | NREL / NLR Electricity Annual Technology Baseline 2025 | Live workbook: https://data.openei.org/files/8759/2025_v1_Workbook_08-27-2026.xlsx (released 2026-08-27). Conservative / Moderate / Advanced scenarios through 2060; docs at https://atb.nlr.gov/electricity/2025/index |
| Utility-scale solar and wind market reports | LBNL | Named in spec; not re-fetched this pass |
| Global renewable cost series | IRENA Renewable Power Generation Costs | Named in spec |
| Global outlook (some detail paywalled) | IEA World Energy Outlook | Unsure flag in spec still stands for detailed datasets |

## Gaps that stay open

- IEA detail behind WEO: may stay paywalled; EIA + ATB + GCP cover a full US-first energy–climate v0.1 without it.
- Reputation and community parameters in Spec §17 remain "from chat, to verify" and do not block the energy build.

## Filled 2026-10-13

- Proved reserves: EIA Form EIA-23L year-end 2024 tables (seed_reserves.csv).
- Capacity builds and retirements: EIA Form EIA-860 2024 generator file aggregated by technology (seed_capacity_860.csv).
- CO2 per unit of fuel: EIA coefficients released 2024-09-18 (seed_co2_coefficients.csv).
- Cost of capital into energy builds: proxy bands from NREL ATB 2025 financial assumptions (AEO-based and ReEDS) plus FRED Baa and 10-year Treasury history 2010-2025 (seed_cost_of_capital.csv). Replace with the economy sector's endogenous rate once that model runs.

## Suggested first pull for v0.1 energy

1. MER CSV tables for fossil and renewable production/consumption and end-use prices (recent decade).
2. ATB 2025 workbook rows for utility PV, land-based wind, and battery storage under Moderate and Advanced.
3. GCP remaining-budget and fossil-emissions pair as the climate gap seed.

That is enough to stand up stocks (reserves, clean capacity, accounting rate), the R1 learning loop, and the B1 cheap-fuel loop with the accounting-rate stabilizer.
