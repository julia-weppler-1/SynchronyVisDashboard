import plotly.graph_objects as go
import plotly as plt
import datetime as dt
import numpy as np
import pandas as pd

# Identify the columns to be used
TS_COL = "timestamp"                # identifies the timestamp column
CJE_COL = "cje"                     # identifies the coordinated joint engagement (CJE) column
SJE_COL = "sje"                     # identifies the shared joint engagement (SJE) column

# Define choices for engagement column creation
CHOICES = [
    1,   # sje = 1 then new value = 1
    2    # cje = 1 then new value = 2
]

# Color Scheme for Behavioral Engagement
    # 0: No Engagement, 1: SJE, 2: CJE
BEHAVIOR_COLORS = [
    [0.0,  "rgb(235,206,203)"],         # for z = 0; No Engagement
    [0.5,  "rgb(230, 140, 130)"],       # for z = 1; SJE
    [1.0,  "rgb(217,89,108)"],          # for z = 2; CJE
]

def make_behavior_heat(df, minimal=False):
    df = df.copy()

    # Define conditions for engagement calculation
    CONDITION = [
        (df["sje"] == 1) & (df["timestamp"].notna()),                  # condition 1: if sje = 1 and timestamp exists
        (df["cje"] == 1) & (df["timestamp"].notna())                   # condition 2: if cje = 1 and timestamp exists
    ]

    # Create engagement column based on conditions (0: No Engagement, 1: SJE, 2: CJE)
    df["engagement"] = np.select(       
        CONDITION,                                              # sets the conditions to check
        CHOICES,                                                # defines output values for each condition
        default=np.where(df["timestamp"].notna(), 0, np.nan)    # sets 0 only if timestamp exists, otherwise leave blank
    )

    df = df.sort_values("timestamp").reset_index(drop=True)    

    engagement = ["Engagement"]                 # y = identifies Engagment as the title for the row(s) in the heat map (y order must match z order of z)
    times = df['timestamp']                     # x = identifies timestamp as the x axis measure
    values = df[["engagement"]].T.to_numpy()    # z = idenitifies values for each row of the heatmap from the df .T.to_numpy() to transpose column to row

    fig = go.Figure(data=go.Heatmap(
            z=values,
            x=times,
            y=engagement,
            zmin=0,                        
            zmax=2,                         
            colorscale=BEHAVIOR_COLORS,    
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

    fig.update_layout(
        margin=dict(l=40, r=8, t=4, b=16),
        autosize=True,
        height=40,
        paper_bgcolor="rgba(0,0,0,0)",     
        plot_bgcolor="rgba(0,0,0,0)",      
        dragmode=False                    
    )
    fig.update_xaxes(
        tickfont=dict(size=8),
        showgrid=False,
    )
    fig.update_yaxes(
        tickfont=dict(size=11),
        showgrid=False,
    )
    fig.update_layout(font=dict(family="Lato, sans-serif"))


    return fig
