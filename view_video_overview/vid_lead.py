import plotly.graph_objects as go
import plotly as plt
import datetime as dt
import numpy as np
import pandas as pd

# Identify the columns to be used
TS_COL = "timestamp"                # identifies the timestamp column
LF_COL = "lf_coh"                   # identifies the low frequency coherence column
HF_COL = "hf_coh"                   # identifies the high frequeny coherence column

# Color Scheme for Leading Dyad
    # 1:C = Child Leading, 2:P = Parent Leading
    # White for 0 (no leading), Green for 1 (Child Leading), Blue for 2 (Parent Leading)
    # needed to make on a scale from 0 to 1 for colors, so set 0, 0.5, 1.0; in heatmap set zmin=0, zmax=2 to match leading_num values
LEAD_COLORS = [
    [0.0,  "rgb(255, 255, 255)"],   # for z = 0
    [0.5,  "rgb(136,218,111)"],     # for z = 1
    [1.0,  "rgb(35,119,180)"],      # for z = 2
]

def make_lead_heat(df, minimal=False):
    df = df.copy()

    for col in [LF_COL, HF_COL]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)                          
    df = df.sort_values("timestamp").reset_index(drop=True)                                    

    df["leading_num"] = df["leading"].str.upper().map({"C": 1, "P": 2}).fillna(0).astype(int)  

    lead = ["Leading"]                          # y = identifies leading_num as the rows in the heat map (y order must match z order of z)
    times = df['timestamp']                     # x = identifies timestamp as the x axis measure
    values = df[["leading_num"]].T.to_numpy()   # z = idenitifies values for each row of the heatmap from the df .T.to_numpy() to transpose column to row

    fig = go.Figure(data=go.Heatmap(
            z=values,
            x=times,
            y=lead,
            zmin=0,                        
            zmax=2,                         
            colorscale=LEAD_COLORS,         
            showscale=False))              

    fig.update_layout(
        margin=dict(l=40, r=8, t=4, b=16),
        autosize=True,
        height=40,
        showlegend=False,                 
        paper_bgcolor="rgba(0,0,0,0)",    
        plot_bgcolor="rgba(0,0,0,0)",       
        dragmode=False                      
    )

    fig.update_xaxes(
        tickfont=dict(size=8),
        showgrid=False,
        showticklabels=False,
        showline=False,
    )
    fig.update_yaxes(
        tickfont=dict(size=10),
        showgrid=False,
        showticklabels=True,
        showline=False,
    )
    fig.update_layout(font=dict(family="Lato, sans-serif"))


    return fig
