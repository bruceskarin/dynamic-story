# dynamic-story
Our understanding of the cosmos is dynamic. Our stories need to be too.

Dynamic Story builds stories about the future that are grounded in real data and get revised as the evidence changes. **Version Zero** is the first public draft: a short core text, a bank of story beats, a simulation spec that couples eleven sectors (plus a thin space layer) through one or two numbers each, and a first runnable sector model (energy). Every figure marked **PROPOSED** or **to verify** is a placeholder awaiting review.

## Repo map

```
docs/
  version-zero.md               Core text, v0.1.0 (nine sections, ending with the Community Layer)
  story-bank.md                 Story beats grouped by theme
  simulation-spec.md            Sector-by-sector spec, coupling table, reputation math, data needs
  coupling-diagram.png          How the sectors connect
  data-availability-energy.md   Public data sources for the energy sector
data/
  README.md                     What each seed file is and where it came from
  seed_*.csv                    Cleaned seed data used by the models
  build_seed.py                 Rebuilds the seed CSVs from raw/
  build_cost_of_capital.py      Rebuilds seed_cost_of_capital.csv
  raw/                          Untouched source downloads (two large EIA-860 files are not committed; see data/README.md)
model/
  energy_v0_1.py                Energy sector v0.1 (US, 2025-2060, stock-and-flow in plain Python)
  README.md                     Structure, results, PROPOSED values, known omissions
  out/                          Summary table, run CSVs and charts for each US budget-share option
```

## Quick start

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
cd model && python energy_v0_1.py      # writes model/out/
```

To rebuild the seed data: `cd data && python build_seed.py && python build_cost_of_capital.py` (the Form 860 step needs the large raw files listed in `data/README.md`).

## Status

Version Zero v0.1.0. Energy is the only runnable sector so far; the politics sector in the spec is built around the Institutional Corruption model in [bruceskarin/blog](https://github.com/bruceskarin/blog). The model uses a sliding US share of the global 2C carbon budget by default (2025 emissions share converging to population share by 2050); see `model/README.md` for results under each option.

## License

CC0 1.0 Universal (see `LICENSE`).
