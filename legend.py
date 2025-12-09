import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

SYNCH_COLORS = px.colors.sequential.BuPu 

LEAD_COLORS = {
    "Child": "rgb(136,218,111)",    # light green
    "Parent": "rgb(35,119,180)"     # dark blue
}

BEHAVIOR_COLORS = {
    "No Engagement": "rgb(235,206,203)",                    # soft rose
    "Supported Joint Engagement (SJE)": "rgb(230,140,130)", # warm coral rose
    "Coordinated Joint Engagement (CJE)": "rgb(217,89,108)" # coral raspberry
}


def make_combined_legend():
    # 2 main columns: left = gradient, right = single vertical stack
    fig = make_subplots(
        rows=1,
        cols=2,
        column_widths=[0.12, 0.88],    # narrow gradient column
        horizontal_spacing=0.2,       # more gap between columns
        subplot_titles=None,
    )

    # Synchrony gradient (left column)
    n_steps = 60
    synch_values = [[i / n_steps] for i in range(n_steps + 1)]

    fig.add_trace(
        go.Heatmap(
            z=synch_values,
            x=[0.5],                     # single column of data
            y=list(range(n_steps + 1)),
            colorscale="BuPu",
            showscale=False,
            zmin=0,
            zmax=1,
            hoverinfo="skip",
        ),
        row=1,
        col=1,
    )

    # Give space on the left for labels
    fig.update_xaxes(
        showticklabels=False,
        showgrid=False,
        zeroline=False,
        range=[-1.0, 1.0],              # extra space at left for labels
        row=1,
        col=1,
    )
    fig.update_yaxes(
        showticklabels=False,
        showgrid=False,
        zeroline=False,
        range=[0, n_steps],
        row=1,
        col=1,
    )

    # Gradient bar occupies x in [0, 1] (within that axis); card sees it as narrow
    bar_left = 0.0
    bar_right = 1.0

    # border around the gradient bar
    fig.add_shape(
        type="rect",
        xref="x1",
        yref="y1",
        x0=bar_left,
        x1=bar_right,
        y0=0,
        y1=n_steps,
        line=dict(color="black", width=1),
        fillcolor="rgba(0,0,0,0)",
        layer="above",
    )

    # Labels to the left of the bar
    label_x = -0.1
    for y, txt in [
        (n_steps, "High Synchrony"),
        (n_steps / 2, "Low Synchrony"),
        (0, "No Synchrony"),
    ]:
        fig.add_annotation(
            x=label_x,
            y=y,
            xref="x1",
            yref="y1",
            text=txt,
            showarrow=False,
            xanchor="right",
            align="right",
            font=dict(size=12),
        )

    # Right column: one vertical stack, grouped into two sections
    leader_labels = [
        "Parent Leading Synchrony",
        "Child Leading Synchrony",
    ]
    leader_colors = [
        LEAD_COLORS["Parent"],
        LEAD_COLORS["Child"],
    ]

    behavior_labels = [
        "Coordinated Joint Engagement (CJE)",
        "Supported Joint Engagement (SJE)",
        "No Engagement",
    ]
    behavior_colors = [
        BEHAVIOR_COLORS["Coordinated Joint Engagement (CJE)"],
        BEHAVIOR_COLORS["Supported Joint Engagement (SJE)"],
        BEHAVIOR_COLORS["No Engagement"],
    ]

    # Larger vertical spacing: two "big rows"
    # big row 1: y = 4–5 (leaders)
    # gap
    # big row 2: y = 1–2 (behaviors)
    y_leader = [4.6, 3.6]
    y_behavior = [2.0, 1.0, 0.0]

    fig.update_xaxes(
        showticklabels=False,
        showgrid=False,
        zeroline=False,
        range=[0, 1],
        row=1,
        col=2,
    )
    fig.update_yaxes(
        showticklabels=False,
        showgrid=False,
        zeroline=False,
        range=[-0.5, 5.8],    # extra headroom for section titles
        row=1,
        col=2,
    )

    box_x = 0.05
    text_x = 0.12           # more room between square and text

    # Leader boxes
    fig.add_trace(
        go.Scatter(
            x=[box_x] * len(y_leader),
            y=y_leader,
            mode="markers",
            marker=dict(
                symbol="square",
                size=16,
                color=leader_colors,
                line=dict(color="gray", width=1),
            ),
            showlegend=False,
            hoverinfo="skip",
        ),
        row=1,
        col=2,
    )

    # Leader labels
    for y, txt in zip(y_leader, leader_labels):
        fig.add_annotation(
            x=text_x,
            y=y,
            xref="x2",
            yref="y2",
            text=txt,
            showarrow=False,
            xanchor="left",
            align="left",
            font=dict(size=12),
        )

    # Section title for leaders
    fig.add_annotation(
        x=0,
        y=5.4,
        xref="x2",
        yref="y2",
        text="Leader In Synchrony",
        showarrow=False,
        xanchor="left",
        font=dict(size=14),
    )

    # Behavior boxes
    fig.add_trace(
        go.Scatter(
            x=[box_x] * len(y_behavior),
            y=y_behavior,
            mode="markers",
            marker=dict(
                symbol="square",
                size=16,
                color=behavior_colors,
                line=dict(color="gray", width=1),
            ),
            showlegend=False,
            hoverinfo="skip",
        ),
        row=1,
        col=2,
    )

    # Behavior labels
    for y, txt in zip(y_behavior, behavior_labels):
        fig.add_annotation(
            x=text_x,
            y=y,
            xref="x2",
            yref="y2",
            text=txt,
            showarrow=False,
            xanchor="left",
            align="left",
            font=dict(size=12),
        )

    # Section title for behaviors (with a gap between sections)
    fig.add_annotation(
        x=0,
        y=2.8,
        xref="x2",
        yref="y2",
        text="Observed Engagement",
        showarrow=False,
        xanchor="left",
        font=dict(size=14),
    )


    fig.update_layout(
        showlegend=False,
        height=180,
        autosize=True,  # responsive; width comes from dcc.Graph
        margin=dict(l=80, r=10, t=15, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        dragmode=False,
        font=dict(family="Lato, sans-serif"),
    )

    return fig
