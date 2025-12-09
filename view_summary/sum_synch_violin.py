import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import datetime as dt 
from plotly.subplots import make_subplots

# Identify the columns to be used
TS_COL = "timestamp"                # identifies the timestamp column
LF_COL = "lf_coh"                   # identifies the low frequency coherence column
HF_COL = "hf_coh"                   # identifies the high frequeny coherence column

OUTLINE_COLOR = 'rgb(140, 107, 177)'      # lighter purple color from 'BuPu' colorscale for violin plot outline
LINE_COLOR = 'rgb(85, 4, 83)'             # darkest color from 'BuPu' colorscale for violin plot outline and inner boxplot
VIOLIN_COLOR = 'rgb(191, 211, 230, 0.75)' # light blue from 'BuPu' colorscale for the fill of the violin plot


def make_violin(df): 
    for col in [LF_COL, HF_COL]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)       
    df = df.sort_values("timestamp").reset_index(drop=True)                

    # Calculate mean and median for hover info
    lf_mean = df["lf_coh"].mean()
    lf_median = df["lf_coh"].median()
    hf_mean = df["hf_coh"].mean()
    hf_median = df["hf_coh"].median()

    # Create subplots: 1 row, 2 columns
    fig = make_subplots(
        rows=1, cols=2,                                     # 1 row, 2 columns (1 row of 2 plots)  
        shared_yaxes=True,                                  
        subplot_titles=("High Frequency Synchrony", "Low Frequency Synchrony"),    
        horizontal_spacing=0.05,
    )

    fig.add_trace(                                       
        go.Violin(
            y=df["lf_coh"],
            name='',
            fillcolor=VIOLIN_COLOR,                       
            line_color=OUTLINE_COLOR,                     
            marker=dict(color=LINE_COLOR, opacity=0.5),   
            box_visible=True,                            
            meanline_visible=True,                       
            points="all",                                 
            jitter=0.2,                                   
            hoveron="points",                           
            hovertemplate=(
            "Value: %{y:.3f}<br>"
            f"Mean: {lf_mean:.3f}<br>"
            f"Median: {lf_median:.3f}"
            "<extra></extra>"
           )
        ),
        row=1, col=2                                  
    )

    # HF coherence violin
    fig.add_trace(
        go.Violin(
            y=df["hf_coh"],
            name='',
            fillcolor=VIOLIN_COLOR,                      
            line_color=OUTLINE_COLOR,                     
            marker=dict(color=LINE_COLOR, opacity=0.5),  
            box_visible=True,                           
            meanline_visible=True,                   
            points="all",                           
            jitter=0.2,                            
            hoveron="points",                         
            hovertemplate=(                           
            "Value: %{y:.3f}<br>"
            f"Mean: {hf_mean:.3f}<br>"
            f"Median: {hf_median:.3f}"
            "<extra></extra>"                              
            ),
        
        ),
        row=1, col=1
    )
    
    fig.update_xaxes(
        showgrid=False,             
        gridcolor="lightgray",     
        title_text="",           
        linecolor="lightgray",  
        linewidth=1,
        showticklabels=False,  
        range=[-0.5, 0.5]       
        )

    fig.update_yaxes(
        showgrid=True, 
        gridcolor="lightgray", 
        title_text="",
        linecolor="lightgray",     
        title_standoff=15,
        linewidth=1)

    fig.update_yaxes(range=[0, 1], title_text="Coherence magnitude", row=1, col=1)

    fig.update_layout(
        title="Synchrony Magnitude Distributions",
        font=dict(color="black"),
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",    
        paper_bgcolor="rgba(0,0,0,0)",   
        autosize=True,                 
        margin=dict(l=90, r=30, t=55, b=0), 
        hovermode="closest",                
        dragmode=False                      
    )

    fig.add_shape(
        type="line",
        xref="x", yref="y",         
        x0=-0.5, y0=0.5,            
        x1=0.5, y1=0.5,             
        line=dict(color=LINE_COLOR, width=2, dash="dash"),
        #row=1, col=1
    )

    
    fig.add_shape(
        type="line",
        xref="x2", yref="y2",     
        x0=-0.5, y0=0.5,           
        x1=0.5, y1=0.5,           
        line=dict(color=LINE_COLOR, width=2, dash="dash"),
    )

    x_line = np.linspace(-0.55, 0.6, 100) 

    fig.add_trace(
        go.Scatter(
            x=x_line,
            y=[0.5] * len(x_line),
            mode="markers", 
            marker=dict(size=20, color="rgba(0,0,0,0)"), 
            showlegend=False,
            hoverinfo="text",
            text=["<b>Threshold for Meaningful Synchrony</b><br>Value: 0.5"] * len(x_line),
            hoverlabel=dict(bgcolor=OUTLINE_COLOR, font=dict(color="white")),
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=x_line,
            y=[0.5] * len(x_line),
            mode="markers",
            marker=dict(size=20, color="rgba(0,0,0,0)"),
            showlegend=False,
            hoverinfo="text",
            text=["<b>Threshold for Meaningful Synchrony</b><br>Value: 0.5"] * len(x_line),
            hoverlabel=dict(bgcolor=OUTLINE_COLOR, font=dict(color="white")),
        ),
        row=1, col=2
    )
    fig.add_annotation(
        x=1.02,
        y=0.6,
        xref="x2 domain",
        yref="y2",
        text="Meaningful</b><br>Synchrony >0.5",
        showarrow=False,
        font=dict(size=11, color="black"),
        bgcolor="rgba(255,255,255,0.0)",
        align="right",
    )

    fig.update_annotations(
        font=dict(size=14, color="black"),
        selector=dict(text="High Frequency Synchrony") 
    )
    fig.update_annotations(
        font=dict(size=14, color="black"),
        selector=dict(text="Low Frequency Synchrony")
    )
    fig.update_layout(font=dict(family="Lato, sans-serif"))

    return fig

