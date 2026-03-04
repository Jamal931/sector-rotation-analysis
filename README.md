
# S&P 500 Sector Rotation Analysis

A quantitative tool for analyzing business-cycle-driven rotation patterns across all 11 GICS sectors using historical ETF data.

<img width="1451" height="554" alt="Screenshot 2026-03-04 at 12 06 57" src="https://github.com/user-attachments/assets/dbb9e710-21cc-4e32-ab94-8ead67ea66aa" />
live link: file:///Users/jamaludeenmohammed/Desktop/IB%20PREP/financial-analysis-projects/S&P%20500%20PROJECT/output/01_bar_chart.html

<img width="1470" height="609" alt="Screenshot 2026-03-04 at 12 06 43" src="https://github.com/user-attachments/assets/d27374c6-b5b6-41b0-a8aa-de117d4ba863" />
live link: file:///Users/jamaludeenmohammed/Desktop/IB%20PREP/financial-analysis-projects/S&P%20500%20PROJECT/output/04_cumulative_cycle.html

<img width="1470" height="581" alt="Screenshot 2026-03-04 at 12 06 24" src="https://github.com/user-attachments/assets/5745a735-4bf7-44b4-8d8b-b7ffe88abedd" />
live link: file:///Users/jamaludeenmohammed/Desktop/IB%20PREP/financial-analysis-projects/S&P%20500%20PROJECT/output/05_rolling_lines.html

---

## What This Does

This project pulls historical price data for the 11 Select Sector SPDR ETFs (XLB (Materials), XLC(Communication Services), XLE(Energy), XLF(Finance), XLI(Industrials), XLK(Technology), XLP(Consumer Staples), XLRE (Real Estate), XLU (Utilities), XLV ( Health Care), XLY ( Consumer Discretionary) ), representing every GICS sector in the S&P 500. It then:

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
