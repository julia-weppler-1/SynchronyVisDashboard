import numpy as np
import pandas as pd
from pathlib import Path
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

TS_COL = "timestamp"
LF_COL = "lf_coh"
HF_COL = "hf_coh"
BU_PU = px.colors.sequential.BuPu

center_x = 0.5  
GLYPH_Y_MIN = 0.05
GLYPH_Y_MAX = 0.95

center_y = (GLYPH_Y_MIN + GLYPH_Y_MAX) / 2.0 # midpoint of y domain
outer_r  = (GLYPH_Y_MAX - GLYPH_Y_MIN) / 2.0 # half the vertical span
inner_r  = outer_r * 0.65 # inner radius is 65% of outer
GAP = 0.02 # how wide the vertical gap is between the donuts

# number of segments the chart is divided into (for gradient)
N_SEG_HALF = 300

def get_color(t):
    t = float(np.clip(t, 0.0, 1.0))
    return px.colors.sample_colorscale(BU_PU, [t])[0]

def half_donut_segments(v):
    # Build (values, colors) for a half-circle gradient donut.
    # The first N_SEG_HALF slices cover 180° (the visible arch).
    # The remaining N_SEG_HALF slices are fully transparent.
    # Within the visible half, t in [0,1] runs from bottom to top.
    # t <= v : gradient color else t > v : transparent.

    v = float(np.clip(v, 0.0, 1.0))

    total_slices = 2 * N_SEG_HALF
    values = [1] * total_slices
    colors = []

    # number of colored slices in the visible half
    n_colored = int(np.ceil(v * N_SEG_HALF))

    # for each slice in visible half (bottom to top)
    for i in range(N_SEG_HALF):
        t = (i + 0.5) / N_SEG_HALF         # compute its normalized position t along the half-arc
        if i < n_colored:
            colors.append(get_color(t))    # color it within visible gradient
        else:
            colors.append("rgba(0,0,0,0)") # points above the coherence val v

    # hidden half: always transparent
    for i in range(N_SEG_HALF):
        colors.append("rgba(0,0,0,0)")

    return values, colors

def make_coherence_figure(df: pd.DataFrame) -> go.Figure:
    df = df.copy()

    for col in [LF_COL, HF_COL]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
    labels = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist()

    lf0 = float(df.iloc[0][LF_COL])
    hf0 = float(df.iloc[0][HF_COL])

    lf_vals, lf_cols = half_donut_segments(lf0)
    hf_vals, hf_cols = half_donut_segments(hf0)

    fig = go.Figure()

    # 1st layer: Background half-donuts (white fill, black outline)
    bg_vals = [1, 1]  # 2 slices = 180° visible + 180° transparent

    # Left background
    fig.add_trace(
        go.Pie(
            values=bg_vals,  
            marker=dict(
                colors=["white", "white"],
                line=dict(color="black", width=2),
            ),
            hole=0.65,  
            sort=False,
            textinfo="none",
            showlegend=False,
            hoverinfo="skip",
            domain=dict(x=[0, 1], y=[GLYPH_Y_MIN, GLYPH_Y_MAX]),
        )
    )

    # Right background
    fig.add_trace(
        go.Pie(
            values=bg_vals,
            marker=dict(
                colors=["white", "white"],
                line=dict(color="black", width=2),
            ),
            hole=0.65,
            sort=False,
            textinfo="none",
            hoverinfo="skip",
            showlegend=False,
            domain=dict(x=[0, 1], y=[GLYPH_Y_MIN, GLYPH_Y_MAX]),
        )
    )

    # 2nd Layer: Actual bars

    # Left side
    fig.add_trace(
        go.Pie(
            values=lf_vals,
            marker=dict(
                colors=lf_cols,
                line=dict(color="white", width=0),
            ),
            hole=0.65,
            sort=False,
            direction="clockwise",   # direction of movement around circle
            rotation=180,            # rotate 180 degrees from start
            textinfo="none",
            hoverinfo="skip",
            showlegend=False,
            domain=dict(
                x=[0, 1],
                y=[GLYPH_Y_MIN, GLYPH_Y_MAX],
            ),
        )
    )

    # Right side
    fig.add_trace(
        go.Pie(
            values=hf_vals,
            marker=dict(colors=hf_cols, line=dict(color="white", width=0)),
            hole=0.65,
            sort=False,
            direction="counterclockwise",  # opposite movement
            rotation=180,
            textinfo="none",
            hoverinfo="skip",
            showlegend=False,
            domain=dict(
                x=[0, 1],
                y=[GLYPH_Y_MIN, GLYPH_Y_MAX],
            ),
        )
    )

    # Labels and total plot sizing
    fig.update_layout(
        autosize=True,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        annotations=[
            dict(
                text="Low Frequency",
                x=0.25, y=GLYPH_Y_MAX + 0.12,
                xanchor="center", yanchor="top",
                showarrow=False
            ),
            dict(
                text="High Frequency",
                x=0.75, y=GLYPH_Y_MAX + 0.12,
                xanchor="center", yanchor="top",
                showarrow=False
            )
        ]
    )

    # 3rd Layer: tick marks to make the backgrounds have end/beginning

    # Left: start tick on left edge of gap
    fig.add_shape(
        type="line",
        x0=center_x - GAP/2,    # outer edge of the gap
        x1=center_x - GAP/2,
        y0=center_y - outer_r,  # bottom of bar
        y1=center_y - inner_r,  # top of bar
        line=dict(color="black", width=2),
        layer="above",
    )
    fig.add_shape(
        type="line",
        x0=center_x - GAP/2,
        x1=center_x - GAP/2,
        y0=center_y + inner_r,
        y1=center_y + outer_r,
        line=dict(color="black", width=2),
        layer="above",
    )
    fig.add_shape(
        type="line",
        x0=center_x + GAP/2,
        x1=center_x + GAP/2,
        y0=center_y - outer_r,
        y1=center_y - inner_r,
        line=dict(color="black", width=2),
        layer="above",
    )
    fig.add_shape(
        type="line",
        x0=center_x + GAP/2,  # opposite edge of gap
        x1=center_x + GAP/2,
        y0=center_y + inner_r,
        y1=center_y + outer_r,
        line=dict(color="black", width=2),
        layer="above",
    )

    # 4th layer: white line down center to visually separate the 2 halfs
    fig.add_shape(
        type="line",
        x0=0.5, x1=0.5,
        y0=GLYPH_Y_MIN - 0.5,
        y1=GLYPH_Y_MAX + 0.5,
        line=dict(color="white", width=5)
    )
    fig.update_layout(font=dict(family="Lato, sans-serif"))

    return fig
