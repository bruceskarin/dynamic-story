# Energy v0.1 (draft simulation)

First runnable pass at Simulation Spec §2, built 2026-10-14 on the seed data in `../data/`. US-first, annual reporting, quarter-year steps, 2025 to 2060. Plain Python (pandas, matplotlib) so it runs on the box; the structure is stock-and-flow so it can be ported to Vensim next to the politics model.

Run: `python energy_v0_1.py` (writes `out/summary.csv`, `out/runs_share_*.csv`, `out/energy_v0_1_*.png`). Needs pandas and matplotlib (see the top-level `requirements.txt`). Each run covers all three US budget-share options; pass `us_share=` to `run()` to pick one, and `slide_end_year=` to move the sliding end point.

## Structure

- Stocks: oil and gas proved reserves (871 quads from EIA-23L 2024), clean capacity (17.0 quads, renewables plus nuclear, MER 2025), cumulative clean built, carbon accounting rate ($/tCO2, starts at 0), cumulative US energy CO2.
- R1 learning: cost falls 15% per doubling of cumulative clean built, scaled by the cost of capital (ATB 2025 real WACC band).
- B1 cheap fuel: fossil price index moves with fossil demand; the accounting rate is added per ton of CO2, so the coal-heavy part of the mix pays more per Btu, and it does not fall with the pump price.
- Accounting-rate rule (Spec §2, §16): rises when the gap is positive or emissions are still growing, eases only when emissions are falling. The gap compares current emissions with the US budget spread evenly to 2050.
- Calibration check: with no accounting rate, clean share goes from 17.7% to 24.1% by 2060, about the same pace as 2010 to 2025 in the MER data (15.1% to 17.7%). Base-year US energy CO2 comes out at 5.28 Gt, roughly 10% above what EPA usually reports, because non-combustion uses of petroleum and gas are not netted out yet.

## Result that matters

The answer depends almost entirely on how the global 2C budget (1110 GtCO2, GCB 2024) is split to the US. There are three options; **sliding is the default** (chosen 2026-10-19).

- `emissions`: the US keeps its 2025 share of world fossil CO2 (14.1%).
- `population`: the US gets its population share (4.2%, PROPOSED).
- `sliding` (default): contraction and convergence. The share moves linearly from 14.1% in 2025 to 4.2% by `slide_end_year` (2050, PROPOSED) and stays there. The global budget is assumed to be spent evenly from 2025 to the 2050 target year, and the US is allotted that year's share of each year's slice, so the US budget is the global budget times the average share over 2025 to 2050 (9.16%, about 102 Gt). This reading is PROPOSED.

Middle accounting path:

| US share | Effective share | US budget | Rate 2035 | Clean share 2060 | Budget exhausted |
|---|---|---|---|---|---|
| Sliding, 14.1% to 4.2% by 2050 (default) | 9.16% | 102 Gt | $43/t | 78% | 2045 |
| 2025 emissions share | 14.1% | 157 Gt | $10/t | 39% | 2055 |
| Population share | 4.2% | 47 Gt | $375/t | 90% | 2035 |

Sliding default across accounting paths (rate 2035 / clean share 2060 / budget exhausted): low $13/t, 55%, 2044; middle $43/t, 78%, 2045; high $101/t, 86%, 2047. With no accounting rate, the sliding budget runs out in 2044.

Under the emissions share, the reactive rule sits near zero for 30 years and then spikes after the budget is gone (too little, too late). Under the population share, it climbs early and steeply. The sliding default lands between them: the rate builds slowly through the 2030s, the budget still runs out in the mid-2040s on every path, and the rate then climbs steeply after that (about $980/t by 2060 on the middle path). Full table in `out/summary.csv`; charts in `out/energy_v0_1_sliding.png`, `_emissions.png` and `_population.png`.

## Proposed values to review

Everything marked PROPOSED in the code: demand growth 0.4%/yr (until transport and housing feed demand), learning rate 15%, cost floor 35%, choice sensitivity 2, build adjustment 8 years, build cap 12%/yr, clean life 35 years, fuel share of fossil cost 50%, price response 0.8, coal price $2/MMBtu, scenario gains (low 3, middle 10, high 25 $/t per year per unit gap), the 4.2% population share, the 2050 end year for the sliding share, and the even-spend reading of the sliding budget.

## Known omissions

No fuel switching inside fossil (coal to gas), no coal reserves stock, no separate electricity versus fuels split, non-combustion uses not netted, and the climate feed is a fixed budget rather than the climate sector model. Spec ambiguity: "still growing" is read as emissions growing; reading it as the gap growing (`growth_test="gap"`) gives almost the same result here.
