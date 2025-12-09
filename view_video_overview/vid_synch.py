import plotly.graph_objects as go
import plotly as plt
import datetime as dt
import numpy as np
import pandas as pd

# Identify the columns to be used
TS_COL = "timestamp"                # identifies the timestamp column
LF_COL = "lf_coh"                   # identifies the low frequency coherence column
HF_COL = "hf_coh"                   # identifies the high frequeny coherence column

def make_synch_heat(df, minimal=False):
    df = df.copy()

    for col in [LF_COL, HF_COL]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)      
    df = df.sort_values("timestamp").reset_index(drop=True)                 
    labels = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist()      
    synch = ["Low Frequency", 'High Frequency'] # y = identifies lf_coh and hf_coh as the rows in the heat map (y order must match z order of z)
    times = df['timestamp']                     # x = identifies timestamp as the x axis measure      
    values = df[[LF_COL, HF_COL]].T.to_numpy()  # z = idenitifies values for each row of the heatmap from the df .T.to_numpy() to transpose column to row
    
    fig = go.Figure(
        data=go.Heatmap(
            z=values,
            x=times,
            y=synch,
            zmin=0,                             
            zmax=1,                             
            colorscale="BuPu",
            showscale=False,                  
        )
    )

    fig.update_layout(
        margin=dict(l=40, r=8, t=4, b=16),
        autosize=True,
        height=80,
        paper_bgcolor="rgba(0,0,0,0)",    
        plot_bgcolor="rgba(0,0,0,0)",       
        dragmode=False                   
    )
    fig.update_xaxes(
        showticklabels=False,
        showgrid=False,
    )
    fig.update_yaxes(
        tickfont=dict(size=10),
        showgrid=False,
    )
    fig.update_layout(font=dict(family="Lato, sans-serif"))


    return fig