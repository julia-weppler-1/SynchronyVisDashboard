import pandas as pd
import numpy as np
import plotly.express as px

LF_COL = "lf_coh"
HF_COL = "hf_coh"
THRESH = 0.5
LEAD_COL = "leading"


def make_synch_bar(df):
   
    df[LEAD_COL] = df[LEAD_COL].astype(str).str.strip()

    # An event is defined as a contiguous sequence of True values in the mask
        # mask helps identify synchrony moments (coherence >= 0.5) and specifically finds when those moments start, so the code can count who was leading at those critical transition points
    def find_event_starts(mask):
        starts = []
        in_run = False

        for i, value in enumerate(mask):
            if value and not in_run:
                starts.append(i)
                in_run = True
            elif not value and in_run:
                in_run = False

        return starts

    # Helper function to count leaders at event starts
    def count_leaders(df, mask):
        starts = find_event_starts(mask)
        child_count = 0
        parent_count = 0

        for i in starts:
            leader = df.loc[i, LEAD_COL]
            if leader.startswith("C"):
                child_count += 1
            elif leader.startswith("P"):
                parent_count += 1

        return child_count, parent_count

    hf_mask = df[HF_COL] >= THRESH
    lf_mask = df[LF_COL] >= THRESH

    # count leaders at start of each moment
    hf_child, hf_parent = count_leaders(df, hf_mask)
    lf_child, lf_parent = count_leaders(df, lf_mask)

    data = pd.DataFrame({
        "Frequency": [
            "High Frequency Synchrony", "High Frequency Synchrony",
            "Low Frequency Synchrony",  "Low Frequency Synchrony",
        ],
        "Leader": ["Child", "Parent", "Child", "Parent"],
        "Count":  [hf_child, hf_parent, lf_child, lf_parent],
    })

    fig = px.bar(
        data,
        x="Leader",
        y="Count",
        color="Leader",
        facet_col="Frequency",
        facet_col_spacing=0.05,
        category_orders={
            "Leader": ["Child", "Parent"],
            "Frequency": ["High Frequency Synchrony", "Low Frequency Synchrony"],
        },
        color_discrete_map={
            "Child": "rgb(136,218,111)",  # light green
            "Parent": "rgb(35,119,180)",  # dark blue
        },
    )

    fig.update_layout(
        title="Synchronous Moments Led by Each Participant",
        showlegend=False,
        margin=dict(l=90, r=30, t=40, b=40),
        plot_bgcolor="white",
        font=dict(color="black")
    )

    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_annotations(font=dict(size=14, color="black",))
    fig.update_xaxes(showgrid=False, 
                     gridcolor="lightgray", 
                     title_text="",
                     showline=True,      
                     linecolor="lightgray",
                     linewidth=1)
    
    fig.update_yaxes(showgrid=True, 
                     gridcolor="lightgray",
                     title_text="",
                     showline=True,
                     linecolor="lightgray",
                     title_standoff=15,
                     linewidth=1)

    fig.layout.yaxis.title.text = "Count"  
    fig.update_layout(font=dict(family="Lato, sans-serif"))

    return fig