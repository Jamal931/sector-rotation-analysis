# =============================================================================
# S&P 500 Sector Rotation Analysis
# Author: Jamaludeen Mohammed
# Description: Pulls historical GICS sector ETF data, calculates rolling
#              returns, and visualizes rotation patterns with business cycle
#              annotations (2020–present).
# =============================================================================

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
import seaborn as sns
import yfinance as yf

warnings.filterwarnings("ignore")

# ── Configuration ─────────────────────────────────────────────────────────────

START_DATE   = "2020-01-01"
END_DATE     = pd.Timestamp.today().strftime("%Y-%m-%d")
ROLLING_WINDOW = 63          # ~1 quarter of trading days
OUTPUT_DIR   = "output"

# All 11 GICS sectors mapped to their Select Sector SPDR ETFs
SECTORS = {
    "XLB":  "Materials",
    "XLC":  "Communication",
    "XLE":  "Energy",
    "XLF":  "Financials",
    "XLI":  "Industrials",
    "XLK":  "Technology",
    "XLP":  "Consumer Staples",
    "XLRE": "Real Estate",
    "XLU":  "Utilities",
    "XLV":  "Health Care",
    "XLY":  "Consumer Discret.",
}

# Business cycle phases with approximate date ranges (2020–present)
# Adjust these as your macro view evolves — this is a key talking point!
CYCLE_PHASES = [
    {"label": "COVID Shock",      "start": "2020-01-01", "end": "2020-04-01", "color": "#FF6B6B"},
    {"label": "Recovery",         "start": "2020-04-01", "end": "2021-01-01", "color": "#FFD93D"},
    {"label": "Expansion",        "start": "2021-01-01", "end": "2022-01-01", "color": "#6BCB77"},
    {"label": "Rate Hike Cycle",  "start": "2022-01-01", "end": "2023-07-01", "color": "#FF6B6B"},
    {"label": "Soft Landing",     "start": "2023-07-01", "end": "2024-09-01", "color": "#FFD93D"},
    {"label": "Late Cycle",       "start": "2024-09-01", "end": END_DATE,     "color": "#4D96FF"},
]

# ── Data Fetching ──────────────────────────────────────────────────────────────

def fetch_sector_data(tickers: list, start: str, end: str) -> pd.DataFrame:
    """Download adjusted closing prices for all sector ETFs."""
    print("Fetching data from Yahoo Finance...")
    raw = yf.download(tickers, start=start, end=end, auto_adjust=True, progress=False)
    prices = raw["Close"]
    prices.columns = [SECTORS[t] for t in prices.columns]  # human-readable names
    prices.dropna(how="all", inplace=True)
    print(f"  ✓ {len(prices)} trading days loaded ({start} → {end})\n")
    return prices

# ── Return Calculations ────────────────────────────────────────────────────────

def calc_rolling_returns(prices: pd.DataFrame, window: int) -> pd.DataFrame:
    """Rolling N-day percentage return for each sector."""
    return prices.pct_change(window).dropna() * 100

def calc_cumulative_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Cumulative return indexed to 100 at start."""
    return (prices / prices.iloc[0]) * 100

def calc_period_returns(prices: pd.DataFrame) -> pd.Series:
    """Total return for the full period."""
    return ((prices.iloc[-1] / prices.iloc[0]) - 1) * 100

# ── Chart 1: Sector Performance Bar Chart ─────────────────────────────────────

def plot_bar_chart(prices: pd.DataFrame, save_dir: str):
    print("Generating: Sector Performance Bar Chart...")
    returns = calc_period_returns(prices).sort_values(ascending=True)

    colors = ["#FF6B6B" if r < 0 else "#6BCB77" for r in returns]

    fig, ax = plt.subplots(figsize=(12, 7))
    bars = ax.barh(returns.index, returns.values, color=colors, edgecolor="white", height=0.6)

    # Label each bar
    for bar, val in zip(bars, returns.values):
        ax.text(
            val + (1.5 if val >= 0 else -1.5),
            bar.get_y() + bar.get_height() / 2,
            f"{val:.1f}%",
            va="center", ha="left" if val >= 0 else "right",
            fontsize=9, color="white", fontweight="bold"
        )

    ax.axvline(0, color="white", linewidth=0.8, linestyle="--", alpha=0.5)
    ax.set_xlabel("Total Return (%)", color="white", fontsize=11)
    ax.set_title(f"S&P 500 Sector Total Returns\n{START_DATE} → {END_DATE}",
                 color="white", fontsize=14, fontweight="bold", pad=15)
    _style_dark(ax, fig)
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, "01_sector_bar_chart.png"), dpi=150)
    plt.close()
    print("  ✓ Saved: 01_sector_bar_chart.png")

# ── Chart 2: Rolling Return Heatmap ───────────────────────────────────────────

def plot_rolling_heatmap(prices: pd.DataFrame, window: int, save_dir: str):
    print("Generating: Rolling Return Heatmap...")
    rolling = calc_rolling_returns(prices, window)

    # Resample to monthly for readability
    monthly = rolling.resample("ME").last().T
    monthly.columns = monthly.columns.strftime("%b %Y")

    fig, ax = plt.subplots(figsize=(22, 7))
    sns.heatmap(
        monthly,
        cmap="RdYlGn",
        center=0,
        linewidths=0.3,
        linecolor="#1a1a2e",
        annot=True,
        fmt=".0f",
        annot_kws={"size": 7},
        cbar_kws={"label": "Rolling Return (%)"},
        ax=ax
    )
    ax.set_title(
        f"Sector Rotation Heatmap — {window}-Day Rolling Returns (Monthly Snapshots)",
        fontsize=13, fontweight="bold", color="white", pad=12
    )
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.tick_params(colors="white", labelsize=8)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    fig.patch.set_facecolor("#1a1a2e")
    ax.set_facecolor("#1a1a2e")
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, "02_rolling_heatmap.png"), dpi=150)
    plt.close()
    print("  ✓ Saved: 02_rolling_heatmap.png")

# ── Chart 3: Correlation Matrix ───────────────────────────────────────────────

def plot_correlation_matrix(prices: pd.DataFrame, save_dir: str):
    print("Generating: Correlation Matrix...")
    daily_returns = prices.pct_change().dropna()
    corr = daily_returns.corr()

    # Mask the upper triangle for a cleaner look
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)

    fig, ax = plt.subplots(figsize=(11, 9))
    sns.heatmap(
        corr,
        mask=mask,
        cmap="coolwarm",
        vmin=-1, vmax=1,
        center=0,
        annot=True,
        fmt=".2f",
        annot_kws={"size": 8},
        linewidths=0.5,
        linecolor="#1a1a2e",
        square=True,
        cbar_kws={"shrink": 0.8, "label": "Pearson Correlation"},
        ax=ax
    )
    ax.set_title(
        "Sector Return Correlations (Daily Returns)\n"
        "Lower correlation = better diversification signal",
        fontsize=13, fontweight="bold", color="white", pad=12
    )
    ax.tick_params(colors="white", labelsize=9)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    fig.patch.set_facecolor("#1a1a2e")
    ax.set_facecolor("#1a1a2e")
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, "03_correlation_matrix.png"), dpi=150)
    plt.close()
    print("  ✓ Saved: 03_correlation_matrix.png")

# ── Chart 4: Cumulative Returns + Business Cycle Annotations ──────────────────

def plot_cumulative_with_cycles(prices: pd.DataFrame, save_dir: str):
    print("Generating: Cumulative Returns + Business Cycle Annotations...")
    cum = calc_cumulative_returns(prices)

    fig, ax = plt.subplots(figsize=(16, 8))

    # ── Shade business cycle phases ──
    legend_patches = []
    seen_labels = set()
    for phase in CYCLE_PHASES:
        s = pd.Timestamp(phase["start"])
        e = pd.Timestamp(phase["end"])
        ax.axvspan(s, e, alpha=0.15, color=phase["color"], zorder=0)
        if phase["label"] not in seen_labels:
            legend_patches.append(
                mpatches.Patch(color=phase["color"], alpha=0.5, label=phase["label"])
            )
            seen_labels.add(phase["label"])
        # Phase label at top
        mid = s + (e - s) / 2
        ax.text(mid, cum.max().max() * 1.01, phase["label"],
                ha="center", va="bottom", fontsize=7.5,
                color=phase["color"], fontweight="bold", rotation=0)

    # ── Plot each sector ──
    cmap = plt.cm.tab20
    for i, col in enumerate(cum.columns):
        ax.plot(cum.index, cum[col], linewidth=1.4,
                color=cmap(i / len(cum.columns)), label=col, alpha=0.9)

    # ── Reference line at 100 ──
    ax.axhline(100, color="white", linewidth=0.6, linestyle="--", alpha=0.4)

    ax.set_ylabel("Indexed Return (Base = 100)", color="white", fontsize=11)
    ax.set_title("S&P 500 Sector Rotation — Cumulative Returns with Business Cycle Phases",
                 color="white", fontsize=14, fontweight="bold", pad=15)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b '%y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

    # Two-column legend: sectors + cycle phases
    sector_legend = ax.legend(loc="upper left", fontsize=8, ncol=2,
                               framealpha=0.2, labelcolor="white")
    ax.add_artist(sector_legend)
    ax.legend(handles=legend_patches, loc="lower right", fontsize=8,
              framealpha=0.2, labelcolor="white", title="Business Cycle",
              title_fontsize=8)

    _style_dark(ax, fig)
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, "04_cumulative_cycle.png"), dpi=150)
    plt.close()
    print("  ✓ Saved: 04_cumulative_cycle.png")

# ── Helpers ────────────────────────────────────────────────────────────────────

def _style_dark(ax, fig):
    """Apply consistent dark theme to a chart."""
    fig.patch.set_facecolor("#1a1a2e")
    ax.set_facecolor("#16213e")
    ax.tick_params(colors="white")
    ax.xaxis.label.set_color("white")
    ax.yaxis.label.set_color("white")
    for spine in ax.spines.values():
        spine.set_edgecolor("#444466")
    ax.grid(axis="both", color="#2a2a4a", linewidth=0.5, linestyle="--")

def save_summary_csv(prices: pd.DataFrame, rolling: pd.DataFrame, save_dir: str):
    """Export summary stats to CSV for further analysis or portfolio use."""
    summary = pd.DataFrame({
        "Total Return (%)":    calc_period_returns(prices).round(2),
        "Avg Rolling Ret (%)": rolling.mean().round(2),
        "Rolling Ret Std (%)": rolling.std().round(2),
        "Sharpe-ish Ratio":    (rolling.mean() / rolling.std()).round(3),
    })
    path = os.path.join(save_dir, "sector_summary.csv")
    summary.to_csv(path)
    print(f"\n  ✓ Summary CSV saved: {path}")
    print("\n" + summary.to_string())

# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    tickers = list(SECTORS.keys())
    prices  = fetch_sector_data(tickers, START_DATE, END_DATE)
    rolling = calc_rolling_returns(prices, ROLLING_WINDOW)

    plot_bar_chart(prices, OUTPUT_DIR)
    plot_rolling_heatmap(prices, ROLLING_WINDOW, OUTPUT_DIR)
    plot_correlation_matrix(prices, OUTPUT_DIR)
    plot_cumulative_with_cycles(prices, OUTPUT_DIR)
    save_summary_csv(prices, rolling, OUTPUT_DIR)

    print(f"\n✅ All outputs saved to /{OUTPUT_DIR}/")

if __name__ == "__main__":
    main()
