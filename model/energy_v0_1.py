"""Dynamic Story, Energy sector v0.1 (draft, US-first, annual).

Stocks: fossil (oil+gas) proved reserves, clean capacity, cumulative clean built
(learning), carbon accounting rate, cumulative US CO2.
Loops: R1 learning, B1 cheap fuel with the accounting rate sitting on it.
Seeds come from ../data/*.csv. Every number not from a seed is marked PROPOSED.
Run: python energy_v0_1.py   (writes out/summary.csv, out/runs_share_*.csv and out/energy_v0_1_*.png)
US budget share options: "sliding" (default), "emissions", "population".
"""
import math, os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "..", "data")
OUT = os.path.join(HERE, "out")

# ---------- seeds ----------
mer = pd.read_csv(os.path.join(D, "seed_mer_annual.csv"))
def m(series, year=2025):
    return float(mer[(mer.series == series) & (mer.year == year)].value.iloc[0])
coal_c = m("Coal Consumption"); gas_c = m("Natural Gas Consumption (Excluding Supplemental Gaseous Fuels)")
oil_c = m("Petroleum Consumption (Excluding Biofuels)")
total_c = m("Total Primary Energy Consumption")
clean0 = m("Total Renewable Energy Consumption") + m("Nuclear Electric Power Consumption")
oilgas_prod = m("Crude Oil Production") + m("Natural Gas Plant Liquids Production") + m("Natural Gas (Dry) Production")
crude_px = m("Crude Oil Domestic First Purchase Price"); gas_px = m("Natural Gas Price, Electric Power Sector")

co2 = pd.read_csv(os.path.join(D, "seed_co2_coefficients.csv")); co2 = co2[co2.unit == "kg CO2 / MMBtu"]
kg = lambda f: float(co2[co2.fuel == f].value.iloc[0])
k_coal, k_gas = kg("Coal (All types)"), kg("Natural Gas")
k_oil = (kg("Finished Motor Gasoline") + kg("Diesel and Home Heating Fuel (Distillate Fuel Oil)") + kg("Jet Fuel")) / 3  # PROPOSED simple petroleum average
fossil0 = coal_c + gas_c + oil_c
mix = {"coal": coal_c / fossil0, "gas": gas_c / fossil0, "oil": oil_c / fossil0}
intensity = (mix["coal"] * k_coal + mix["gas"] * k_gas + mix["oil"] * k_oil) / 1000  # tCO2 per MMBtu

res = pd.read_csv(os.path.join(D, "seed_reserves.csv"))
r = lambda s, y=2024: float(res[(res.series == s) & (res.year == y)].value.iloc[0])
BTU_PER_BBL, BTU_PER_CF = 5.8e6, 1036  # EIA standard conversion factors
q = 1e15
reserves0 = (r("crude_oil_lease_condensate_proved_reserves") * 1e6 * BTU_PER_BBL + r("natural_gas_wet_proved_reserves") * 1e9 * BTU_PER_CF) / q
additions0 = (r("crude_oil_extensions_discoveries") * 1e6 * BTU_PER_BBL + r("natural_gas_extensions_discoveries") * 1e9 * BTU_PER_CF) / q

gcp = pd.read_csv(os.path.join(D, "seed_climate_gap.csv")).set_index("quantity").value
world_fossil = float(gcp["fossil_co2_emissions"])

coc = pd.read_csv(os.path.join(D, "seed_cost_of_capital.csv"))
wacc = lambda band: float(coc[(coc.band == band) & (coc.variable == "wacc_real") & (coc.year == 2025)].value_fraction.iloc[0])

atb = pd.read_csv(os.path.join(D, "seed_atb_clean_costs.csv"))
pv = atb[(atb.technology == "utility_pv") & (atb.metric == "lcoe")]

# ---------- parameters ----------
P = dict(
    start=2025, end=2060, dt=0.25,
    demand_growth=0.004,        # PROPOSED until transport + housing feed demand
    learning_rate=0.15,         # PROPOSED cost drop per doubling of cumulative clean built
    cost_floor=0.35,            # PROPOSED clean cost can't fall below 35% of 2025
    choice_gamma=2.0,           # PROPOSED sensitivity of clean share to cost ratio
    build_adjust_years=8.0,     # PROPOSED time to close gap to desired clean capacity
    max_build_growth=0.12,      # PROPOSED cap on build as fraction of capacity per year
    clean_life=35.0,            # PROPOSED average clean asset life
    fuel_share_of_cost=0.5,     # PROPOSED fuel share of delivered fossil cost
    price_elasticity_inv=0.8,   # PROPOSED B1 price response to fossil demand
    discovery_price_elast=1.0,  # PROPOSED reserve additions respond to price
    capex_share=0.8,            # PROPOSED share of clean LCOE that scales with capital recovery
    wacc_band="atb_aeo",
    budget_level="remaining_co2_budget_2C_50pct",
    us_share="sliding",         # "sliding" (default), "emissions" (2025 share of world fossil CO2), or "population" (PROPOSED 4.2%)
    population_share=0.042,     # PROPOSED US share of world population, used by "population" and as the "sliding" end point
    slide_end_year=2050,        # PROPOSED year the sliding share reaches the population share (linear from the 2025 emissions share)
    target_year=2050,
    rate_gain=0.0,              # $/tCO2 per year per unit gap; scenarios set this
    rate_decay_years=10.0,
    growth_test="emissions",   # spec ambiguity: 'still growing' read as emissions growing (alt: "gap")      # PROPOSED: rate eases only when the gap is closing
)

def crf(r, n=30):
    return r / (1 - (1 + r) ** -n)

def us_share_at(year, p, emis_share0):
    """US share of the global budget in a given year under the chosen option."""
    if p["us_share"] == "emissions":
        return emis_share0
    if p["us_share"] == "population":
        return p["population_share"]
    if p["us_share"] == "sliding":
        span = p["slide_end_year"] - p["start"]
        f = min(max((year - p["start"]) / span, 0.0), 1.0) if span > 0 else 1.0
        return emis_share0 + (p["population_share"] - emis_share0) * f
    raise ValueError(f"unknown us_share {p['us_share']!r}")

def effective_share(p, emis_share0, steps=1000):
    """Budget share used for the fixed US budget.

    For "emissions" and "population" this is the constant share. For "sliding"
    (contraction and convergence) the global budget is assumed to be spent evenly
    from start to target_year, and the US is allotted share(t) of each year's
    slice, so the US budget is the global budget times the average share over
    that window. PROPOSED reading of the sliding option.
    """
    a, b = p["start"], p["target_year"]
    if p["us_share"] != "sliding" or b <= a:
        return us_share_at(a, p, emis_share0)
    h = (b - a) / steps
    return sum(us_share_at(a + (i + 0.5) * h, p, emis_share0) for i in range(steps)) / steps

def run(**over):
    p = {**P, **over}
    dt = p["dt"]
    w0 = wacc("atb_aeo"); w = wacc(p["wacc_band"])
    capital_factor = (1 - p["capex_share"]) + p["capex_share"] * crf(w) / crf(w0)
    us_emis0 = fossil0 * intensity  # GtCO2/yr (quads*1e9 MMBtu * t/MMBtu / 1e9)
    share = effective_share(p, us_emis0 / world_fossil)
    budget = float(gcp[p["budget_level"]]) * share
    fuel_px0 = (oil_c * crude_px / 5.8 + gas_c * gas_px + coal_c * 2.0) / fossil0  # $/MMBtu; coal 2.0 PROPOSED
    delivered0 = fuel_px0 / p["fuel_share_of_cost"]
    s0 = clean0 / total_c
    odds0 = (1 - s0) / s0
    oilgas_share0 = (oil_c + gas_c) / fossil0
    prod_ratio = oilgas_prod / (oil_c + gas_c)
    # stocks
    reserves, clean, cum_built, rate, cum_co2 = reserves0, clean0, clean0, 0.0, 0.0
    prev_emis, prev_gap = us_emis0, -1e9
    rows, t = [], float(p["start"])
    while t <= p["end"] + 1e-9:
        demand = total_c * (1 + p["demand_growth"]) ** (t - p["start"])
        fossil = max(demand - clean, 0.0)
        emis = fossil * intensity                                   # GtCO2/yr
        price_idx = (fossil / fossil0) ** p["price_elasticity_inv"]  # B1
        fuel_px = fuel_px0 * price_idx
        carbon_adder = rate * intensity                              # $/MMBtu, coal-heavy mix pays more per Btu
        fossil_cost = (delivered0 - fuel_px0) + fuel_px + carbon_adder
        clean_cost_idx = max((cum_built / clean0) ** math.log2(1 - p["learning_rate"]), p["cost_floor"]) * capital_factor
        ratio = (fossil_cost / delivered0) / clean_cost_idx
        desired_share = 1 / (1 + odds0 * ratio ** (-p["choice_gamma"]))
        desired_clean = desired_share * demand
        retire = clean / p["clean_life"]
        build = max(min((desired_clean - clean) / p["build_adjust_years"] + retire, p["max_build_growth"] * clean), 0.0)
        extraction = fossil * oilgas_share0 * prod_ratio
        additions = additions0 * price_idx ** p["discovery_price_elast"]
        remaining = max(budget - cum_co2, 0.0)
        years_left = max(p["target_year"] - t, 1.0)
        allowed = remaining / years_left
        gap = min(emis / allowed - 1, 5.0) if allowed > 1e-6 else 5.0
        gap_rising = (gap > prev_gap) if p["growth_test"] == "gap" else (emis > prev_emis)
        if gap > 0 or gap_rising:   # spec: rises when the gap is wide or still growing
            d_rate = p["rate_gain"] * max(gap, 0.1)
        elif emis < prev_emis:      # falls only when the gap is closing
            d_rate = -rate / p["rate_decay_years"]
        else:
            d_rate = 0.0
        if abs(t - round(t)) < 1e-9:
            rows.append(dict(year=int(round(t)), us_share_effective=share, us_share_year=us_share_at(t, p, us_emis0 / world_fossil), demand_quads=demand, clean_quads=clean, fossil_quads=fossil,
                             clean_share=clean / demand, emissions_gt=emis, cum_co2_gt=cum_co2, us_budget_gt=budget,
                             accounting_rate_usd_t=rate, fossil_price_idx=price_idx, clean_cost_idx=clean_cost_idx,
                             oilgas_extraction_quads=extraction, reserves_quads=reserves, gap=gap))
        prev_emis, prev_gap = emis, gap
        reserves += (additions - extraction) * dt
        clean += (build - retire) * dt
        cum_built += build * dt
        rate = max(rate + d_rate * dt, 0.0)
        cum_co2 += emis * dt
        t += dt
    return pd.DataFrame(rows)

SHARES = {"sliding": f"sliding share, 2025 emissions share to {P['population_share']:.1%} by {P['slide_end_year']}",
          "emissions": "2025 emissions share", "population": f"population share, {P['population_share']:.1%}"}  # sliding is the default
SCENARIOS = {"none": 0.0, "low": 3.0, "middle": 10.0, "high": 25.0}  # PROPOSED gains, $/t/yr per unit gap

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    print(f"2025 check: fossil {fossil0:.1f} quads, intensity {intensity*1000:.1f} kgCO2/MMBtu, US energy CO2 {fossil0*intensity:.2f} Gt, "
          f"oil+gas reserves {reserves0:.0f} quads, additions {additions0:.0f} quads/yr, clean {clean0:.1f} quads")
    summary = []
    for share in SHARES:
        frames = []
        for name, g in SCENARIOS.items():
            df = run(rate_gain=g, us_share=share); df["scenario"] = name; frames.append(df)
            base_ext = run(rate_gain=0.0, us_share=share).oilgas_extraction_quads.sum()
            summary.append(dict(us_share=share, scenario=name, effective_share=round(df.us_share_effective.iloc[0], 4), budget_gt=round(df.us_budget_gt.iloc[0], 1),
                                rate_2035=round(df.set_index("year").accounting_rate_usd_t[2035]),
                                rate_2060=round(df.accounting_rate_usd_t.iloc[-1]),
                                clean_share_2040=round(df.set_index("year").clean_share[2040], 3),
                                clean_share_2060=round(df.clean_share.iloc[-1], 3),
                                emissions_2060_gt=round(df.emissions_gt.iloc[-1], 2),
                                cum_co2_2060_gt=round(df.cum_co2_gt.iloc[-1], 1),
                                budget_exhausted_year=(int(df[df.cum_co2_gt >= df.us_budget_gt].year.min()) if (df.cum_co2_gt >= df.us_budget_gt).any() else None),
                                oilgas_left_in_ground_vs_none_quads=round(base_ext - df.oilgas_extraction_quads.sum())))
        pd.concat(frames).to_csv(os.path.join(OUT, f"runs_share_{share}.csv"), index=False)
    s = pd.DataFrame(summary); s.to_csv(os.path.join(OUT, "summary.csv"), index=False)
    print(s.to_string(index=False))
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    for share, label in SHARES.items():
        df = pd.read_csv(os.path.join(OUT, f"runs_share_{share}.csv"))
        fig, ax = plt.subplots(2, 2, figsize=(11, 7))
        for name, g in df.groupby("scenario", sort=False):
            ax[0, 0].plot(g.year, g.emissions_gt, label=name); ax[0, 1].plot(g.year, g.clean_share, label=name)
            ax[1, 0].plot(g.year, g.accounting_rate_usd_t, label=name); ax[1, 1].plot(g.year, g.oilgas_extraction_quads, label=name)
        for a, tt in zip(ax.flat, ["US energy CO2 (Gt/yr)", "Clean share of primary energy", "Accounting rate ($/tCO2)", "Oil+gas extraction (quads/yr)"]):
            a.set_title(tt); a.grid(alpha=.3)
        ax[0, 0].legend(title="accounting path"); fig.suptitle(f"Dynamic Story energy v0.1 draft (US budget = {label} of 2C budget)")
        fig.tight_layout(); fig.savefig(os.path.join(OUT, f"energy_v0_1_{share}.png"), dpi=120); plt.close(fig)
