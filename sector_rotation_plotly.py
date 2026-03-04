# =============================================================================
# S&P 500 Sector Rotation — Interactive Plotly Charts
# Companion to sector_rotation.py — run this for browser-based exploration
# =============================================================================

import os
import warnings
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import yfinance as yf

warnings.filterwarnings("ignore")

# ── Config ─────────────────────────────────────────────────────────────────────

START_DATE     = "2020-01-01"
END_DATE       = pd.Timestamp.today().strftime("%Y-%m-%d")
ROLLING_WINDOW = 63
OUTPUT_DIR     = "output"

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

CYCLE_PHASES = [
    {"label": "COVID Shock",     "start": "2020-01-01", "end": "2020-04-01", "color": "rgba(255,107,107,0.15)"},
    {"label": "Recovery",        "start": "2020-04-01", "end": "2021-01-01", "color": "rgba(255,217,61,0.15)"},
    {"label": "Expansion",       "start": "2021-01-01", "end": "2022-01-01", "color": "rgba(107,203,119,0.15)"},
    {"label": "Rate Hike Cycle", "start": "2022-01-01", "end": "2023-07-01", "color": "rgba(255,107,107,0.15)"},
    {"label": "Soft Landing",    "start": "2023-07-01", "end": "2024-09-01", "color": "rgba(255,217,61,0.15)"},
    {"label": "Late Cycle",      "start": "2024-09-01", "end": END_DATE,     "color": "rgba(77,150,255,0.15)"},
]

BASE_LAYOUT = dict(
    paper_bgcolor="#1a1a2e",
    plot_bgcolor="#16213e",
    font=dict(color="white", family="Inter, Arial, sans-serif"),
)

# ── Data ───────────────────────────────────────────────────────────────────────

def fetch_data():
    print("Fetching data...")
    tickers = list(SECTORS.keys())
    raw = yf.download(tickers, start=START_DATE, end=END_DATE,
                      auto_adjust=True, progress=False)
    prices = raw["Close"]
    prices.columns = [SECTORS[t] for t in prices.columns]
    prices.dropna(how="all", inplace=True)
    print(f"  ✓ {len(prices)} trading days\n")
    return prices

def add_cycle_shading(fig):
    for phase in CYCLE_PHASES:
        fig.add_vrect(
            x0=phase["start"], x1=phase["end"],
            fillcolor=phase["color"],
            layer="below", line_width=0,
            annotation_text=phase["label"],
            annotation_position="top left",
            annotation=dict(font=dict(size=9, color="rgba(255,255,255,0.6)")),
        )

# ── Chart 1: Bar Chart ─────────────────────────────────────────────────────────

def plot_bar_chart(prices):
    print("Building: Interactive Bar Chart...")
    total_ret = ((prices.iloc[-1] / prices.iloc[0]) - 1) * 100
    total_ret = total_ret.sort_values(ascending=True)
    colors = ["#FF6B6B" if v < 0 else "#6BCB77" for v in total_ret]

    fig = go.Figure(go.Bar(
        x=total_ret.values,
        y=total_ret.index,
        orientation="h",
        marker_color=colors,
        text=[f"{v:.1f}%" for v in total_ret.values],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Return: %{x:.2f}%<extra></extra>",
    ))
    fig.add_vline(x=0, line_color="rgba(255,255,255,0.3)", line_dash="dash")
    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text=f"S&P 500 Sector Total Returns ({START_DATE} → {END_DATE})", font=dict(size=16)),
        xaxis=dict(title="Total Return (%)", gridcolor="#2a2a4a", zerolinecolor="#444466"),
        yaxis=dict(gridcolor="#2a2a4a"),
        height=520, showlegend=False,
        margin=dict(l=20, r=80, t=60, b=40),
    )
    path = os.path.join(OUTPUT_DIR, "01_bar_chart.html")
    fig.write_html(path)
    print(f"  ✓ Saved: {path}")

# ── Chart 2: Rolling Heatmap ───────────────────────────────────────────────────

def plot_rolling_heatmap(prices):
    print("Building: Rolling Return Heatmap...")
    rolling = prices.pct_change(ROLLING_WINDOW).dropna() * 100
    monthly = rolling.resample("ME").last().T
    monthly.columns = monthly.columns.strftime("%b %Y")

    fig = go.Figure(go.Heatmap(
        z=monthly.values,
        x=monthly.columns.tolist(),
        y=monthly.index.tolist(),
        colorscale="RdYlGn",
        zmid=0,
        text=[[f"{v:.0f}%" for v in row] for row in monthly.values],
        texttemplate="%{text}",
        textfont=dict(size=8),
        hovertemplate="<b>%{y}</b><br>%{x}<br>Rolling Return: %{z:.1f}%<extra></extra>",
        colorbar=dict(
            title=dict(text="Return (%)", font=dict(color="white")),
            tickfont=dict(color="white"),
        ),
    ))
    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text=f"Sector Rotation Heatmap — {ROLLING_WINDOW}-Day Rolling Returns", font=dict(size=16)),
        xaxis=dict(tickangle=-45, gridcolor="#2a2a4a"),
        yaxis=dict(gridcolor="#2a2a4a"),
        height=420,
        margin=dict(l=20, r=20, t=60, b=80),
    )
    path = os.path.join(OUTPUT_DIR, "02_rolling_heatmap.html")
    fig.write_html(path)
    print(f"  ✓ Saved: {path}")

# ── Chart 3: Correlation Matrix ───────────────────────────────────────────────

def plot_correlation_matrix(prices):
    print("Building: Correlation Matrix...")
    corr = prices.pct_change().dropna().corr().round(2)
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    masked = corr.where(~mask)

    fig = go.Figure(go.Heatmap(
        z=masked.values,
        x=corr.columns.tolist(),
        y=corr.index.tolist(),
        colorscale="RdBu",
        zmid=0, zmin=-1, zmax=1,
        text=[[f"{v:.2f}" if not np.isnan(v) else "" for v in row] for row in masked.values],
        texttemplate="%{text}",
        textfont=dict(size=9),
        hovertemplate="<b>%{y} × %{x}</b><br>Correlation: %{z:.2f}<extra></extra>",
        colorbar=dict(
            title=dict(text="ρ", font=dict(color="white")),
            tickfont=dict(color="white"),
        ),
    ))
    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text="Sector Return Correlations (Daily Returns)", font=dict(size=16)),
        xaxis=dict(tickangle=-45, gridcolor="#2a2a4a"),
        yaxis=dict(gridcolor="#2a2a4a"),
        height=560,
        margin=dict(l=20, r=20, t=60, b=80),
    )
    path = os.path.join(OUTPUT_DIR, "03_correlation_matrix.html")
    fig.write_html(path)
    print(f"  ✓ Saved: {path}")

# ── Chart 4: Cumulative Returns + Business Cycle ──────────────────────────────

def plot_cumulative_with_cycles(prices):
    print("Building: Cumulative Returns + Business Cycle...")
    cum = (prices / prices.iloc[0]) * 100
    colors = px.colors.qualitative.Plotly + px.colors.qualitative.Dark24

    fig = go.Figure()
    for i, col in enumerate(cum.columns):
        fig.add_trace(go.Scatter(
            x=cum.index, y=cum[col], name=col, mode="lines",
            line=dict(width=1.8, color=colors[i % len(colors)]),
            hovertemplate=f"<b>{col}</b><br>%{{x|%b %d, %Y}}<br>Indexed: %{{y:.1f}}<extra></extra>",
        ))
    fig.add_hline(y=100, line_color="rgba(255,255,255,0.25)", line_dash="dash", line_width=1)
    add_cycle_shading(fig)
    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text="S&P 500 Sector Rotation — Cumulative Returns with Business Cycle Phases", font=dict(size=16)),
        xaxis=dict(gridcolor="#2a2a4a", zerolinecolor="#444466"),
        yaxis=dict(title="Indexed Return (Base = 100)", gridcolor="#2a2a4a", zerolinecolor="#444466"),
        height=580, hovermode="x unified",
        legend=dict(bgcolor="rgba(0,0,0,0.4)", bordercolor="#444466", borderwidth=1, font=dict(size=10), x=1.01),
        margin=dict(l=20, r=160, t=60, b=60),
    )
    path = os.path.join(OUTPUT_DIR, "04_cumulative_cycle.html")
    fig.write_html(path)
    print(f"  ✓ Saved: {path}")

# ── Chart 5: Rolling Lines ────────────────────────────────────────────────────

def plot_rolling_lines(prices):
    print("Building: Rolling Returns Line Chart...")
    rolling = prices.pct_change(ROLLING_WINDOW).dropna() * 100
    colors  = px.colors.qualitative.Plotly + px.colors.qualitative.Dark24

    fig = go.Figure()
    for i, col in enumerate(rolling.columns):
        fig.add_trace(go.Scatter(
            x=rolling.index, y=rolling[col].round(2), name=col, mode="lines",
            line=dict(width=1.5, color=colors[i % len(colors)]),
            hovertemplate=f"<b>{col}</b><br>%{{x|%b %d, %Y}}<br>{ROLLING_WINDOW}d Return: %{{y:.1f}}%<extra></extra>",
        ))
    fig.add_hline(y=0, line_color="rgba(255,255,255,0.25)", line_dash="dash", line_width=1)
    add_cycle_shading(fig)
    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text=f"{ROLLING_WINDOW}-Day Rolling Returns by Sector  (click legend to toggle)", font=dict(size=16)),
        xaxis=dict(gridcolor="#2a2a4a", zerolinecolor="#444466"),
        yaxis=dict(title="Rolling Return (%)", gridcolor="#2a2a4a", zerolinecolor="#444466"),
        height=560, hovermode="x unified",
        legend=dict(bgcolor="rgba(0,0,0,0.4)", bordercolor="#444466", font=dict(size=10), x=1.01),
        margin=dict(l=20, r=160, t=60, b=60),
    )
    path = os.path.join(OUTPUT_DIR, "05_rolling_lines.html")
    fig.write_html(path)
    print(f"  ✓ Saved: {path}")

# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    prices = fetch_data()
    plot_bar_chart(prices)
    plot_rolling_heatmap(prices)
    plot_correlation_matrix(prices)
    plot_cumulative_with_cycles(prices)
    plot_rolling_lines(prices)
    print(f"\n✅ All interactive charts saved to /{OUTPUT_DIR}/")
    print("   Open any .html file in your browser — no server needed.")

if __name__ == "__main__":
    main()