import pandas as pd
import numpy as np
import plotly.express as px

CHOICES = [
    1,   # sje = 1 then new value = 1
    2    # cje = 1 then new value = 2
]

# Map engagement numeric values to SHORT labels (for slice labels)
ENG_SHORT = {
    0: 'None',
    1: 'SJE',
    2: 'CJE'
}

# Map engagement numeric values to FULL labels (for legend)
ENG_FULL = {
    0: 'No Joint Engagement',
    1: 'Supported Joint Engagement (SJE)',
    2: 'Coordinated Joint Engagement (CJE)'
}

# Set colors for pie chart
PIE_COLORS = {
    'No Joint Engagement'        : 'rgb(235,206,203)',  # soft rose
    'Supported Joint Engagement (SJE)' : 'rgb(230, 140, 130)',# warm coral rose
    'Coordinated Joint Engagement (CJE)': 'rgb(217,89,108)'   # coral raspberry
}

def make_pie(df):

    CONDITION = [
        (df["sje"] == 1),
        (df["cje"] == 1),
    ]

    df["engagement"] = np.select(CONDITION, CHOICES, default=0)

    counts = df["engagement"].value_counts().sort_index()
    percent = (counts / counts.sum()) * 100

    percent_df = percent.rename("percent").reset_index()
    percent_df.columns = ["engagement_code", "percent"]

    percent_df["engagement_full"] = percent_df["engagement_code"].map(ENG_FULL)
    percent_df["engagement_short"] = percent_df["engagement_code"].map(ENG_SHORT)

    fig = px.pie(
        percent_df,
        values="percent",
        names="engagement_full",
        hole=0.35,
        color="engagement_full",
        color_discrete_map=PIE_COLORS,
        category_orders={
            "engagement_full": [
                "No Joint Engagement",
                "Supported Joint Engagement (SJE)",
                "Coordinated Joint Engagement (CJE)",
            ]
        },
    )

    fig.update_layout(
        title_text=None,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.1,
            xanchor="center",
            x=0.3,
        ),
        margin=dict(l=40, r=40, t=50, b=50),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        autosize=True,
        uniformtext_minsize=10,
        uniformtext_mode="hide",
    )


    fig.update_traces(
        texttemplate="%{percent:.1%}<br>%{customdata}",
        textposition="auto",
        textfont_size=14,
        marker=dict(
            line=dict(
                color="black", 
                width=1.0,
            )
        ),
        hovertemplate="%{label}: %{percent:.1%}<extra></extra>",
        customdata=percent_df["engagement_short"],
    )
    fig.update_layout(font=dict(family="Lato, sans-serif"))

    return fig
