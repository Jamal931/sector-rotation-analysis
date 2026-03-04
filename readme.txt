# S&P 500 Sector Rotation Analysis

A quantitative tool for analyzing business-cycle-driven rotation patterns across all 11 GICS sectors using historical ETF data.

![Cumulative Returns](output/04_cumulative_cycle.png)

---

## What This Does

This project pulls historical price data for the 11 Select Sector SPDR ETFs (XLB, XLC, XLE, XLF, XLI, XLK, XLP, XLRE, XLU, XLV, XLY), representing every GICS sector in the S&P 500. It then:

- Calculates **rolling quarterly returns** to surface rotation trends
- Builds a **sector heatmap** showing which sectors lead/lag each month
- Computes a **correlation matrix** to identify diversification opportunities
- Overlays **business cycle phase annotations** (COVID shock → recovery → expansion → rate hike cycle → soft landing) on cumulative return charts
- Exports a **summary CSV** with total returns, volatility, and a Sharpe-style ratio

---

## Outputs

| File | Description |
|------|-------------|
| `output/01_sector_bar_chart.png` | Total return by sector since Jan 2020 |
| `output/02_rolling_heatmap.png` | 63-day rolling return heatmap (monthly snapshots) |
| `output/03_correlation_matrix.png` | Pearson correlation of daily returns |
| `output/04_cumulative_cycle.png` | Cumulative returns with business cycle shading |
| `output/sector_summary.csv` | Summary stats: total return, avg rolling return, std, Sharpe-ish ratio |

---

## Macro Framework

Sector rotation follows the **business cycle** — different sectors tend to outperform at different phases:

| Phase | Historically Strong Sectors |
|-------|------------------------------|
| Recovery | Consumer Discretionary, Financials, Tech |
| Expansion | Industrials, Materials, Energy |
| Slowdown | Health Care, Consumer Staples |
| Contraction | Utilities, Consumer Staples |

This tool makes those rotations visible in real data.

---

## Setup & Run

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/sector-rotation-analysis.git
cd sector-rotation-analysis

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the analysis
python sector_rotation.py
```

Charts and CSV will be saved to the `output/` folder.

---

## Customization

- **Change time period**: Edit `START_DATE` / `END_DATE` in the config section
- **Change rolling window**: Adjust `ROLLING_WINDOW` (default: 63 trading days ≈ 1 quarter)
- **Update cycle phases**: Edit the `CYCLE_PHASES` list with your own macro interpretations

---

## Tech Stack

- `yfinance` — market data via Yahoo Finance API  
- `pandas` — data manipulation and time series  
- `matplotlib` — charting and annotations  
- `seaborn` — heatmaps and statistical visualization  
- `numpy` — numerical calculations  

---

## Skills Demonstrated

- Financial data engineering (ETF data pipeline)
- Time series analysis (rolling returns, cumulative indexing)
- Macro/fundamental overlay (business cycle framework)
- Data visualization for decision-making
