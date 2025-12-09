from plotly.subplots import make_subplots
import plotly.graph_objects as go
import numpy as np
import pandas as pd

# Import heat maps 
from view_video_overview.vid_behavior import make_behavior_heat
from view_video_overview.vid_lead import make_lead_heat
from view_video_overview.vid_synch import make_synch_heat

from load_data import df

TS_COL = "timestamp"

def make_stacked_heatmaps(minimal=False):  # Function to create stacked heatmaps with shared x-axis
    def _fmt_secs(sec):
        sec = int(round(sec))
        m = sec // 60
        s = sec % 60
        return f"{m}:{s:02d}"

    ts_series = pd.to_datetime(df[TS_COL]).sort_values().reset_index(drop=True)
    t0 = ts_series.iloc[0]

    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,           # share x-axis across heatmaps
        vertical_spacing=0.04,       # reduce space between plots
        row_heights=[0.6, 0.2, 0.2],
    )

    # Build the three base heatmaps
    synch_fig = make_synch_heat(df)         # row 1
    lead_fig = make_lead_heat(df)           # row 2
    behavior_fig = make_behavior_heat(df)   # row 3

    fig.add_trace(synch_fig.data[0], row=1, col=1)
    fig.add_trace(lead_fig.data[0], row=2, col=1)
    fig.add_trace(behavior_fig.data[0], row=3, col=1)

    # set x-axis ticks as mm:ss instead of dt
    n = len(ts_series)
    step = 60  # one tick per 60 samples
    idxs = list(range(0, n, step)) or [0]

    tickvals = ts_series.iloc[idxs]                     # still real timestamps
    ticktext = [_fmt_secs(i) for i in idxs]             # what we show as labels

    fig.update_xaxes(
        tickmode="array",
        tickvals=tickvals,
        ticktext=ticktext,
        row=3,
        col=1,  # bottom axis; shared_xaxes makes it apply visually to all
    )

    # hover tooltips uses video time

    # compute elapsed seconds for each timestamp
    elapsed_secs = (ts_series - t0).dt.total_seconds().round().astype(int)
    elapsed_labels = [_fmt_secs(s) for s in elapsed_secs]

    # We assume all three heatmaps use the same x (timestamps), so index j = elapsed_labels[j].

    # SYNCH HEATMAP 
    synch_z = np.array(synch_fig.data[0].z)        # shape (2, n)
    n_rows, n_cols = synch_z.shape

    synch_row_labels = ["Low Frequency", "High Frequency"]
    synch_custom = []
    for r in range(n_rows):
        row_cd = []
        for c in range(n_cols):
            row_cd.append([elapsed_labels[c], synch_row_labels[r]])
        synch_custom.append(row_cd)

    fig.data[0].update(
        customdata=synch_custom,
        hovertemplate="Time: %{customdata[0]}<br>Signal: %{customdata[1]}<br>Value: %{z:.3f}<extra></extra>"
    )

    # LEAD HEATMAP (trace 1)
    LEAD_MAP = {0: "None", 1: "Child", 2: "Parent"}

    lead_z = np.array(lead_fig.data[0].z)          # shape (1, n)
    _, lead_n_cols = lead_z.shape

    lead_custom = [[
        [elapsed_labels[c], LEAD_MAP.get(int(lead_z[0, c]), int(lead_z[0, c]))]
        for c in range(lead_n_cols)
    ]]

    fig.data[1].update(
        customdata=lead_custom,
        hovertemplate="Time: %{customdata[0]}<br>Leading: %{customdata[1]}<extra></extra>"
    )

    # BEHAVIOR HEATMAP
    BEHAVIOR_MAP = {0: "No Engagement", 1: "Supported Joint Engagement", 2: "Coordinated Joint Engagement"}

    beh_z = np.array(behavior_fig.data[0].z)       # shape (1, n)
    _, beh_n_cols = beh_z.shape

    behavior_custom = [[
        [elapsed_labels[c], BEHAVIOR_MAP.get(int(beh_z[0, c]), int(beh_z[0, c]))]
        for c in range(beh_n_cols)
    ]]

    fig.data[2].update(
        customdata=behavior_custom,
        hovertemplate="Time: %{customdata[0]}<br>%{customdata[1]}<extra></extra>"
    )

    fig.update_layout(
        showlegend=False,
        coloraxis_showscale=False,
        autosize=True,
        margin=dict(l=60, r=20, t=80, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        dragmode=False,
        hovermode="closest",  # avoid unified hover
        font=dict(family="Lato, sans-serif"),
    )

    return fig
