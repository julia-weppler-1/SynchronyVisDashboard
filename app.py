import pandas as pd
from dash import Dash, html, dcc, callback_context
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio
from dash_player import DashPlayer
from dash.dependencies import Input, Output, State, MATCH
from view_point_in_time.pit_synch import make_coherence_figure, half_donut_segments
from view_point_in_time.pit_dyad_lead import make_leading_panel
from view_point_in_time.pit_behavior import make_behavior_panel

from view_summary.sum_behaviors_pie import make_pie
from view_summary.sum_synch_bar import make_synch_bar
from view_summary.sum_synch_violin import make_violin
from view_summary.sum_table import make_summary_table

from vid_heatmaps import make_stacked_heatmaps

from legend import make_combined_legend

#Load Data
from load_data import df, VIDEO


# Color Scheme for the App
    # Synchrony Colors
        # Colors from Plotly's 'BuPu' colorscale

    # Parent/Adult and Child Colors
        # rgb (136,218,111)     # light green   (child)
        # rgb (35,119,180 )     # dark blue     (adult)

    # Behavior Colors
        # 'rgb(235,206,203)' =      'No Engagement'                   # soft rose
        # 'rgb(230, 140, 130)', =   'Supported Joint Engagement'      # warm coral rose
        # 'rgb(217,89,108)' =       'Coordinated Joint Engagement'    # coral raspberry

FONT = [
    "https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,100;0,300;0,400;0,700;0,900;1,100;1,300;1,400;1,700;1,900&display=swap"
]
app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=FONT)

# Creates a consistent card style for all cards in the app
CARD_STYLE = {
    "backgroundColor": "white",
    "border": "1px solid #dcdcdc",
    "borderRadius": "8px",
    "padding": "12px",
    "boxShadow": "0 1px 3px rgba(0,0,0,0.06)",
    "position": "relative",
}

TAB_BASE_STYLE = {
    "display": "flex",
    "alignItems": "center",
    "justifyContent": "center",
    "padding": "4px 10px",
    "borderRadius": "999px",        # pill shape
    "border": "2px solid #333",
    "cursor": "pointer",
    "gap": "6px",                    # space between icon and text
}


ICON_BASE_STYLE = {
    "width": "18px",
    "height": "18px",
}

FIG_SYNCH_GLYPH        = make_coherence_figure(df)

FIG_LEADING_PANEL      = make_leading_panel(df, row_index=1)
FIG_BEHAVIOR_PANEL     = make_behavior_panel(df, row_index=1)

FIG_SYNCH_BAR          = make_synch_bar(df)
FIG_SYNCH_BAR.update_layout(clickmode="event+select")
FIG_VIOLIN             = make_violin(df)
TABLE_SUMMARY          = make_summary_table(df)
FIG_PIE                = make_pie(df)
BASE_PLAY_HEATMAP = make_stacked_heatmaps(minimal=False).update_layout(margin=dict(l=90, r=20, t=10, b=30))

LEAD_COL = "leading"
TS_COL = "timestamp"
LF_COL = "lf_coh"
HF_COL = "hf_coh"

DEFAULT_FONT = "Lato, sans-serif"
SYNCH_COLORS = px.colors.sequential.BuPu 

lato_template = pio.templates["plotly_white"]
lato_template.layout.font.family = DEFAULT_FONT

pio.templates["lato"] = lato_template
pio.templates.default = "lato"

TS_SERIES = pd.to_datetime(df[TS_COL]) 
VIDEO_START = TS_SERIES.iloc[0]

sample_fig = make_stacked_heatmaps(minimal=False)
heatmap_tickvals = sample_fig.layout.xaxis.tickvals
heatmap_ticktext = sample_fig.layout.xaxis.ticktext

# Convert heatmap ticks to slider marks for the range slider
if heatmap_tickvals is not None and heatmap_ticktext is not None:
    SLIDER_MARKS = {
        int((pd.to_datetime(tick) - TS_SERIES.min()).total_seconds()): {
            "label": text,
            "style": {"fontSize": "9px", "whiteSpace": "nowrap"}
        }
        for tick, text in zip(heatmap_tickvals, heatmap_ticktext)
    }
else:
    # Fallback if ticks aren't set
    SLIDER_MARKS = {
        int((t - TS_SERIES.min()).total_seconds()): {
            "label": t.strftime("%Y-%m-%d %H:%M:%S"),
            "style": {"fontSize": "12px", "whiteSpace": "nowrap"}
        }
        for t in pd.date_range(TS_SERIES.min(), TS_SERIES.max(), freq='2min')
    }

def chart_header(title: str, index: str, body: str):
    # index: string per chart (“summary”, “pie”, “timeline”)
    # body:  text explaining what the chart is / how to use it
    return html.Div(
        style={
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "space-between",
            "marginBottom": "4px",
            "gap": "8px",
        },
        children=[
            html.Span(
                title,
                style={"fontWeight": "bold"},
            ),

            # info icon
            html.Span(
                "?",
                id={"type": "info-icon", "index": index},
                n_clicks=0,
                style={
                    "display": "inline-flex",
                    "alignItems": "center",
                    "justifyContent": "center",
                    "width": "18px",
                    "height": "18px",
                    "borderRadius": "50%",
                    "border": "1px solid #999",
                    "fontSize": "12px",
                    "fontWeight": "600",
                    "cursor": "pointer",
                    "color": "#555",
                    "backgroundColor": "#f9f9f9",
                    "flexShrink": 0,
                    "userSelect": "none",
                },
            ),

            # tooltip 
            html.Div(
                id={"type": "info-tooltip", "index": index},
                style={
                    "display": "none",        # toggled by callback
                    "position": "absolute",
                    "right": "10px",
                    "top": "32px",
                    "zIndex": 999,            # layer order
                    "backgroundColor": "white",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "boxShadow": "0 4px 12px rgba(0,0,0,0.10)",
                    "padding": "10px 12px",
                    "fontSize": "12px",
                    "lineHeight": "1.4",
                },
                children=[
                    html.Div(
                        "About this chart",
                        style={
                            "fontWeight": "600",
                            "marginBottom": "4px",
                        },
                    ),
                    html.Div(body),
                ],
            ),
        ],
    )

def make_synchrony_gradient_legend():
    # For PIT legend gradient
    n_steps = 60
    synch_values = [[i / n_steps] for i in range(n_steps + 1)]

    fig = make_subplots(rows=1, cols=1)

    # Bar from y=0..n_steps
    fig.add_trace(
        go.Heatmap(
            z=synch_values,
            x=[0.0],
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

    pad_frac = 0.01
    pad = pad_frac * n_steps

    axis_range_x = [-3.0, 3.0]
    bar_left, bar_right = -0.5, 0.5

    fig.update_xaxes(
        showticklabels=False,
        showgrid=False,
        zeroline=False,
        range=axis_range_x,
        row=1,
        col=1,
    )
    fig.update_yaxes(
        showticklabels=False,
        showgrid=False,
        zeroline=False,
        # bar is 0..n_steps, axis is slightly bigger
        range=[-pad, n_steps + pad],
        row=1,
        col=1,
    )

    # Border around the bar 
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

    # Labels at 0 / mid / n_steps
    label_x = -2.0
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

    fig.update_layout(
        showlegend=False,
        autosize=True,
        margin=dict(l=80, r=8, t=34, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        dragmode=False,
        font=dict(family="Lato, sans-serif"),
    )

    return fig


def make_timeline_fig_with_default_window(idx: int = 0):
    # Base stacked heatmap with an initial highlight band + cursor line
    # centered on the row at idx (default = first sample)
    base = (
        make_stacked_heatmaps(minimal=False)
        .update_xaxes(domain=[0.05, 1.0])
        .update_layout(margin=dict(l=90, r=20, t=0, b=0))
    )

    cursor_time = TS_SERIES.iloc[idx]
    half_window = pd.Timedelta(seconds=30)

    window_start = max(TS_SERIES.iloc[0], cursor_time - half_window)
    window_end   = min(TS_SERIES.iloc[-1], cursor_time + half_window)

    base.update_layout(
        shapes=[
            dict(
                type="rect",
                x0=window_start,
                x1=window_end,
                y0=0,
                y1=1,
                xref="x",
                yref="paper",
                fillcolor="rgba(255, 230, 128, 0.35)",
                line=dict(color="rgba(255, 196, 0, 0.9)", width=1),
                layer="above",
            ),
            dict(
                type="line",
                x0=cursor_time,
                x1=cursor_time,
                y0=0,
                y1=1,
                xref="x",
                yref="paper",
                line=dict(color="black", width=3),
            ),
        ]
    )

    return base


def home_layout(show_pit: bool = False):
    # When show_pit is False:
        # Layout like mockup 1 (no visible PIT cards).
    # When show_pit is True:
        # Layout like mockup 2 (PIT cards on the left).

    if not show_pit:
        return html.Div(
            style={
                "display": "grid",
                "gridTemplateColumns": "0.9fr 0.5fr 1.2fr",
                "gridTemplateRows": "minmax(320px, auto) minmax(180px, auto)",
                "gridTemplateAreas": """
                    "summary summary rightcol"
                    "legend  timeline timeline"
                """,
                "gap": "16px",
                "alignItems": "stretch",
            },
            children=[
                # Hidden PIT so callbacks have targets
                html.Div(
                    style={"display": "none"},
                    children=[
                        dcc.Graph(
                            id="synch-glyph",
                            figure=FIG_SYNCH_GLYPH,
                        ),
                        html.Div(id="dyad-leading-panel", children=FIG_LEADING_PANEL),
                        html.Div(id="dyad-behavior-panel", children=FIG_BEHAVIOR_PANEL),
                    ],
                ),

                # big summary (cols 1–2, row 1) 
                html.Div(
                    style={**CARD_STYLE, "gridArea": "summary"},
                    children=[
                        chart_header(
                            title="Physiologic Synchrony Summary",
                            index="synch-summary",
                            body=(
                                "This panel displays who led synchronous moments and the distribution of synchry strength ",
                                "from the recorded session. The top bar chart indicates how many times each participant led a synchronous",
                                " moment in both low and high-frequency synchrony (with a cutoff magnitude of 0.5). If there is no data for a participant, it means",
                                " they did not lead a synchronous moment for that frequency. Clicking on a participant's bar will filter ",
                                "the visuals for percent of time in joint engagement and synchrony magnitude distributions by synchronies (low or high) led by the selected participant.",
                                " Clicking again will remove the filter.",
                            ),
                        ),

                        dcc.Graph(
                            id="leading-behaviors",
                            figure=FIG_SYNCH_BAR,
                            style={"height": "260px", "marginTop": "4px"},
                            config={"displayModeBar": False},
                        ),
                        dcc.Graph(
                            id="synchrony-violin",
                            figure=FIG_VIOLIN,
                            style={
                                "height": "260px",
                                "marginTop": "4px",
                                "marginBottom": "2px",
                            },
                            config={"displayModeBar": False},
                        ),
                    ],
                ),

                # right column (col 3, row 1)
                html.Div(
                    style={
                        "gridArea": "rightcol",
                        "display": "flex",
                        "flexDirection": "column",
                        "gap": "16px",
                        "height": "100%", 
                    },
                    children=[
                        html.Div(
                            style={**CARD_STYLE},
                            children=[
                                chart_header(
                                    title="Summary Table",
                                    index="summary-table",
                                    body=(
                                        "This table provides a takeaway summary of the session data, including the total number of synchronous ",
                                        "moments, the average duration of each synchronous moment, the number of moments of engagement (including both coordinated and",
                                        " supported join engagement), and the average duration of engagements. A threshold of 0.5 was used to discern synchronous versus ",
                                        "non-synchronous moments."
                                    ),
                                ),
                                html.Div(
                                    id="summary-table",
                                    children=TABLE_SUMMARY,
                                ),
                            ],
                        ),
                        html.Div(
                            style={
                                **CARD_STYLE,
                                "flex": "1",
                                "display": "flex",
                                "flexDirection": "column",
                            },
                            children=[
                                chart_header(
                                    title="Percent of Time in Joint Engagement",
                                    index="engagement-pie",
                                    body=(
                                        "This chart shows the percentage of time participants spent in different engagement states "
                                        "(No Joint Engagement, Supported Joint Engagement, Coordinated Joint Engagement). "
                                        "Use it to understand how much of the session involves shared attention."
                                    ),
                                ),
                                dcc.Graph(
                                    id="engagement-pie-chart",
                                    figure=FIG_PIE,
                                    style={"width": "100%", 
                                           "height": "100%"},
                                    config={"responsive": True, 
                                            "displayModeBar": False},
                                ),
                            ],
                        ),

                    ],
                ),

                # legend (col 1, row 2)
                html.Div(
                    style={
                        **CARD_STYLE,
                        "gridArea": "legend",
                    },
                    children=[
                        html.Div(
                            "Legend",
                            style={"fontWeight": "bold", "marginBottom": "2px"},
                        ),  
                        dcc.Graph(
                            figure=make_combined_legend(),
                            id="legend",
                            config={
                                "displayModeBar": False,
                                "staticPlot": True,
                            },
                            style={
                                "maxWidth": "500px",
                                "minWidth": "400px",
                                "height": "210px",
                                "margin": "0 auto",
                            },
                        ),
                    ],
                ),

                # heatmaps (cols 2–3, row 2)
                html.Div(
                    style={**CARD_STYLE, "gridArea": "timeline"},
                    children=[
                        chart_header(
                                title="Parent-Child Session Data of Physiologic Synchrony, Leading Behavior, and Engagment",
                                index="vid-heatmaps",
                                body=(
                                    "The stacked heatmaps displayed in this section represent an overview of the sensor and behavioral",
                                    " data collected during the session. The color of each vertical line in the heatmap represents the value",
                                    " (such as the amount of synchrony) at one second. The timestamps displayed at the bottom correspond to the video",
                                    " timestamps from the recording session. Clicking once on the stacked heatmaps will open a one-minute interval window ",
                                    "that filters the data displayed in synchrony magnitude distributions and percent of time in joint engagement.",
                                    " When Point-in-time views is enabled, the balck vertical line will also update the position of the point-in-time physiologic synchrony and ",
                                    "parent-child interactions card. Clicking again will remove the brushing window."
                                ),
                        ),
                        html.Div(
                            style={
                                "display": "flex",
                                "flexDirection": "column",
                                "gap": "0",
                                "marginTop": "4px",
                            },
                            children=[
                                dcc.Graph(
                                    id="timeline-heatmap",
                                    figure=(
                                        make_stacked_heatmaps(minimal=False)
                                        .update_xaxes(domain=[0.05, 1.0])
                                        .update_layout(
                                            margin=dict(l=90, r=20, t=0, b=0)
                                        )
                                    ),
                                    style={
                                        "height": "220px",
                                        "margin": "0",
                                        "padding": "0",
                                    },
                                    config={"displayModeBar": False},
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        )

    # PIT on
    return html.Div(
        style={
            "display": "grid",
            "gridTemplateColumns": "0.9fr 1.4fr 1.1fr",
            "gridTemplateRows": "minmax(180px, auto) minmax(180px, auto) minmax(180px, auto)",
            "gridTemplateAreas": """
                "pit    summary rightcol"
                "dyad   summary rightcol"
                "legend timeline timeline"
            """,
            "gap": "16px",
            "alignItems": "stretch",
        },
        children=[
            # PIT synch (top-left)
            html.Div(
                style={**CARD_STYLE, "gridArea": "pit"},
                children=[
                    chart_header(
                            title="Point-in-Time Physiologic Synchrony",
                            index="pit-synch",
                            body=(
                                "The dual radial bar charts depict the magnitude of low frequency synchrony and high ",
                                "frequency synchrony at each second in the data. The time at which the data is displayed is updated by the black cursor bar ",
                                "within in stacked heatmaps (Parent-Child Session Data) at the bottom of this dashbaord. When the cursor is toggled off (via click), the ",
                                "radial bar charts show the synchrony magnitudes at the first second of the collected data.",
                                " Both the length and color of the bars indicate the magnitude of synchrony - short, lighter bars represent a lack of synchrony, bars that reach a bluish tint ",
                                "at the midway point represent low synchrony, and very long bars reaching a deep purple represent high synchrony. "
                            ),
                    ),
                    html.Div(
                        style={
                            "display": "grid",
                            "gridTemplateColumns": "minmax(160px, 0.6fr) 1.4fr",
                            "alignItems": "stretch",
                            "height": "100%",
                            "columnGap": "8px",
                        },
                        children=[
                            # gradient legend
                            html.Div(
                                children=dcc.Graph(
                                    id="pit-synch-legend",
                                    figure=make_synchrony_gradient_legend(),
                                    config={"displayModeBar": False, "staticPlot": True},
                                    style={
                                        "width": "100%",
                                        "minHeight" : "270px",
                                        "maxHeight": "75%",  
                                        "margin": "0",
                                    },
                                ),
                                style={
                                    "display": "flex",
                                    "alignItems": "stretch",
                                    "justifyContent": "flex-start",
                                },
                            ),
                            # synchrony glyph
                            html.Div(
                                style={
                                    "display": "flex",
                                    "alignItems": "stretch", 
                                    "justifyContent": "center",
                                },
                                children=dcc.Graph(
                                    id="synch-glyph",  
                                    figure=FIG_SYNCH_GLYPH,
                                    style={
                                        "width": "100%",
                                        "minHeight" : "270px",
                                        "maxHeight": "75%", 
                                        "margin": "0",
                                    },
                                    config={"displayModeBar": False},
                                ),
                            ),
                        ],
                    ),
                ],
            ),

            # PIT interactions / behaviors (middle-left)
            html.Div(
                style={
                    **CARD_STYLE,
                    "gridArea": "dyad",
                    "display": "flex",
                    "flexDirection": "column",
                    "maxHeight": "350px",  
                    "overflow": "hidden",
                },
                children=[
                    chart_header(
                            title="Parent-Child Interactions",
                            index="pit-interactions",
                            body=(
                                "This card displays the behavioral data collected from the recording session,"
                                " including the parent-child engagement and who is leading the synchrony (parent or child).",
                                " The time at which the data is displayed is updated by the black cursor bar ",
                                "within in stacked heatmaps (Parent-Child Session Data) at the bottom of this dashbaord. When the cursor is toggled off (via click), the ",
                                "cards show the behaviors at the first second of the collected data. The engagement card is coordinated to the bottom 'Engagement' heatmap",
                                " and displays what type of engagement (if any) is occurring at the selected time. The right icon under Leading Phsyicologic Synchrony is ",
                                " coordinated to the 'Leading' heatmap and indicates whether the parent or child is leading the interaction at that moment."
                            ),
                    ),
                    html.Div(
                        style={
                            # side-by-side layout like Play view
                            "display": "grid",
                            "gridTemplateColumns": "1fr 1fr",
                            "alignItems": "center",
                            "justifyItems": "center",
                            "columnGap": "12px",
                            "marginTop": "8px",
                            "height": "100%",
                        },
                        children=[
                            html.Div(
                                id="dyad-behavior-panel",
                                children=FIG_BEHAVIOR_PANEL,
                                style={
                                    "width": "90%",
                                    "maxWidth": "220px",
                                    "margin": "0 auto",
                                },
                            ),
                            html.Div(
                                id="dyad-leading-panel",
                                children=FIG_LEADING_PANEL,
                                style={
                                    "width": "90%",
                                    "maxWidth": "220px",
                                    "margin": "0 auto",
                                },
                            ),
                        ],
                    ),
                ],
            ),

            # big summary (center column)
            html.Div(
                style={**CARD_STYLE, "gridArea": "summary"},
                children=[
                    chart_header(
                            title="Physiologic Synchrony Summary",
                            index="synch-summary",
                            body=(
                                "This panel displays who led synchronous moments and the distribution of synchry strength ",
                                "from the recorded session. The top bar chart indicates how many times each participant led a synchronous",
                                " moment in both low and high-frequency synchrony (with a cutoff magnitude of 0.5). If there is no data for a participant, it means",
                                " they did not lead a synchronous moment for that frequency. Clicking on a participant's bar will filter ",
                                "the visuals for percent of time in joint engagement and synchrony magnitude distributions by synchronies (low or high) led by the selected participant.",
                                " Clicking again will remove the filter.",
                            ),
                    ),
                    dcc.Graph(
                        id="leading-behaviors",
                        figure=FIG_SYNCH_BAR,
                        style={"height": "260px", "marginTop": "4px"},
                        config={"displayModeBar": False},
                    ),
                    dcc.Graph(
                        id="synchrony-violin",
                        figure=FIG_VIOLIN,
                        style={
                            "height": "260px",
                            "marginTop": "4px",
                            "marginBottom": "2px",
                        },
                        config={"displayModeBar": False},
                    ),
                ],
            ),

            # right column: summary table + summary behaviors
            html.Div(
                style={
                    "gridArea": "rightcol",
                    "display": "flex",
                    "flexDirection": "column",
                    "gap": "16px",
                    "height": "100%", 

                },
                children=[
                    html.Div(
                        style={**CARD_STYLE},
                        children=[
                            chart_header(
                                    title="Summary Table",
                                    index="summary-table",
                                    body=(
                                        "This table provides a takeaway summary of the session data, including the total number of synchronous ",
                                        "moments, the average duration of each synchronous moment, the number of moments of engagement (including both coordinated and",
                                        " supported join engagement), and the average duration of engagements. A threshold of 0.5 was used to discern synchronous versus ",
                                        "non-synchronous moments."
                                    ),
                                ),
                            html.Div(
                                id="summary-table",
                                children=TABLE_SUMMARY,
                            ),
                        ],
                    ),
                    html.Div(
                        style={
                            **CARD_STYLE,
                            "flex": "1",               
                            "display": "flex",
                            "flexDirection": "column",
                        },
                        children=[
                            chart_header(
                                title="Percent of Time in Joint Engagement",
                                index="engagement-pie",
                                body=(
                                    "This chart shows the percentage of time participants spent in different engagement states "
                                    "(No Joint Engagement, Supported Joint Engagement, Coordinated Joint Engagement). "
                                    "Use it to understand how much of the session involves shared attention."
                                ),
                            ),
                            dcc.Graph(
                                id="engagement-pie-chart",
                                figure=FIG_PIE,
                                style={
                                    "width": "100%",
                                    "height": "100%",
                                },
                                config={
                                    "responsive": True,
                                    "displayModeBar": False,
                                },
                            ),
                        ],
                    ),
                ],
            ),

            # legend bottom-left
            html.Div(
                style={
                    **CARD_STYLE,
                    "gridArea": "legend",
                    "display": "flex",
                },
                children=[
                    html.Div(
                        "Legend",
                        style={"fontWeight": "bold", "marginBottom": "4px"},
                    ),
                    dcc.Graph(
                        figure=make_combined_legend(),
                        id="legend",
                        config={
                            "displayModeBar": False,
                            "staticPlot": True,
                        },
                        style={
                            "maxWidth": "500px",
                            "minWidth": "400px",
                            "height": "210px",
                            "margin": "0 auto",
                        },
                    ),
                ],
            ),

            # heatmaps bottom (cols 2–3)
            html.Div(
                style={**CARD_STYLE, "gridArea": "timeline"},
                children=[

                    chart_header(
                            title="Parent-Child Session Data of Physiologic Synchrony, Leading Behavior, and Engagment",
                            index="vid-heatmaps",
                            body=(
                                    "The stacked heatmaps displayed in this section represent an overview of the sensor and behavioral",
                                    " data collected during the session. The color of each vertical line in the heatmap represents the value",
                                    " (such as the amount of synchrony) at one second. The timestamps displayed at the bottom correspond to the video",
                                    " timestamps from the recording session. Clicking once on the stacked heatmaps will open a one-minute interval window ",
                                    "that filters the data displayed in synchrony magnitude distributions and percent of time in joint engagement.",
                                    " When Point-in-time views is enabled, the balck vertical line will also update the position of the point-in-time physiologic synchrony and ",
                                    "parent-child interactions card. Clicking again will remove the brushing window."
                                ),
                    ),
                    html.Div(
                        style={
                            "display": "flex",
                            "flexDirection": "column",
                            "gap": "0",
                            "marginTop": "4px",
                        },
                        children=[
                            dcc.Graph(
                                id="timeline-heatmap",
                                figure=make_timeline_fig_with_default_window(idx=0),
                                style={
                                    "height": "220px",
                                    "margin": "0",
                                    "padding": "0",
                                },
                                config={"displayModeBar": False},
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )

# method for the play tab
def play_layout():
    return html.Div(
        style={
            "display": "grid",
            "gridTemplateColumns": "0.7fr 1.8fr",
            "gridTemplateRows": "minmax(150px, auto) minmax(240px, auto) minmax(160px, auto)",
            "gridTemplateAreas": """
                "pit    playmain"
                "dyad   playmain"
                "legend playmain"
            """,
            "gap": "8px",
            "backgroundColor": "#f5f5f5",
            "alignItems": "stretch",
        },
        children=[
            # PIT synch card 
            html.Div(
                style={**CARD_STYLE, "gridArea": "pit"},
                children=[
                    chart_header(
                            title="Point-in-Time Physiologic Synchrony",
                            index="pit-synch",
                            body=(
                                "The dual radial bar charts depict the magnitude of low frequency synchrony and high ",
                                "frequency synchrony at each second in the video. The time at which the data is displayed is updated by navigating or playing the video.  ",
                                " Both the length and color of the bars indicate the magnitude of synchrony - short, lighter bars represent a lack of synchrony, bars that reach a bluish tint ",
                                "at the midway point represent low synchrony, and very long bars reaching a deep purple represent high synchrony. "
                            ),
                    ),
                    html.Div(
                        style={
                            "display": "grid",
                            "gridTemplateColumns": "minmax(160px, 0.6fr) 1.4fr",
                            "alignItems": "stretch",  
                            "height": "100%",
                            "columnGap": "8px",
                        },
                        children=[
                            # gradient legend
                            html.Div(
                                children=dcc.Graph(
                                    id="pit-synch-legend",
                                    figure=make_synchrony_gradient_legend(),
                                    config={"displayModeBar": False, "staticPlot": True},
                                    style={
                                        "width": "100%",
                                        "minHeight" : "270px",
                                        "maxHeight": "75%",  
                                        "margin": "0",
                                    },
                                ),
                                style={
                                    "display": "flex",
                                    "alignItems": "stretch",   
                                    "justifyContent": "flex-start",
                                },
                            ),
                            # synchrony glyph
                            html.Div(
                                style={
                                    "display": "flex",
                                    "alignItems": "stretch", 
                                    "justifyContent": "center",
                                },
                                children=dcc.Graph(
                                    id="synch-glyph-play",
                                    figure=FIG_SYNCH_GLYPH,
                                    style={
                                        "width": "100%",
                                        "minHeight" : "270px",
                                        "maxHeight": "75%", 
                                        "margin": "0",
                                    },
                                    config={"displayModeBar": False},
                                ),
                            ),
                        ],
                    ),
                ],
            ),

            # Dyad interactions card 
            html.Div(
                style={
                    **CARD_STYLE,
                    "gridArea": "dyad",
                    "display": "flex",
                    "flexDirection": "column",
                    "overflow": "hidden",
                },
                children=[
                    chart_header(
                            title="Parent-Child Interactions",
                            index="pit-interactions",
                            body=(
                                "This card displays the behavioral data collected from the recording session,"
                                " including the parent-child engagement and who is leading the synchrony (parent or child).",
                                " The time at which the data is displayed is updated by the video. The engagement card is coordinated to the bottom 'Engagement' heatmap",
                                " and displays what type of engagement (if any) is occurring at the selected time. The right icon under Leading Phsyicologic Synchrony is ",
                                " coordinated to the 'Leading' heatmap and indicates whether the parent or child is leading the interaction at that moment."
                            ),
                    ),
                    html.Div(
                        style={
                            "display": "grid",
                            "gridTemplateColumns": "1.2fr 0.8fr",
                            "alignItems": "center",
                            "justifyItems": "center",
                            "columnGap": "12px",
                            "marginBottom": "8px",
                            "height": "100%",
                        },
                        children=[
                            html.Div(
                                children=html.Img(
                                    id="behavior-play-img",
                                    src="/assets/behav_NoJE.png",   # default
                                    title="No Joint Engagement",
                                    style={
                                        "width": "90%",
                                        "height": "auto",
                                    },
                                ),
                            ),
                            html.Div(
                                children=html.Img(
                                    id="leader-play-img",
                                    src="/assets/lead_parent.png",  # default
                                    style={
                                        "width": "100%",
                                        "maxWidth": "240px",
                                        "height": "auto",
                                    },
                                ),
                            ),
                        ],
                    ),
                ],
            ),

            # Combined Legend card
            html.Div(
                style={
                    **CARD_STYLE,
                    "gridArea": "legend",
                    "display": "flex",
                },
                children=[
                    html.Div(
                        "Legend",
                        style={"fontWeight": "bold", "marginBottom": "4px"},
                    ),
                    dcc.Graph(
                        figure=make_combined_legend(),
                        id="legend-play",
                        config={
                            "displayModeBar": False,
                            "staticPlot": True,
                        },
                        style={
                            "maxWidth": "500px",
                            "minWidth": "400px",
                            "height": "210px",
                            "margin": "0 auto",
                        },
                    ),
                ],
            ),

            # Main Play area 
            html.Div(
                style={**CARD_STYLE, "gridArea": "playmain", "padding": "8px"},
                children=[
                    chart_header(
                            title="Play View",
                            index="vid-playback",
                            body=(
                                "This is the video playback panel of the recorded session. Playing the",
                                " video will update the black cursor below, indicating the corresponding point in the heatmaps. It will also",
                                " update the data displayed on the left of the video to provide more detail on the information represented ",
                                "in the heatmaps."
                            ),
                    ),
                    html.Div(
                        style={
                            "display": "flex",
                            "flexDirection": "column",
                            "gap": "8px",
                        },
                        children=[
                            html.Div(
                                style={"flex": "0 0 auto"},
                                children=DashPlayer(
                                    id="video-player",
                                    url=VIDEO,
                                    controls=True,
                                    playing=False,
                                    width="100%",
                                    height="auto",
                                ),
                            ),
                            html.Div(
                                style={
                                    "flex": "0 0 auto",
                                    "height": "220px",
                                    "borderRadius": "0",
                                    "overflow": "hidden",
                                },
                                children=dcc.Graph(
                                    id="play-heatmap-stack",
                                    figure=BASE_PLAY_HEATMAP,
                                    style={
                                        "height": "100%",
                                        "width": "100%",
                                        "margin": "0",
                                    },
                                    config={"displayModeBar": False},
                                ),
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )

# Prebuild layouts once
HOME_LAYOUT = home_layout()
PLAY_LAYOUT = play_layout()

# Main app layout
app.layout = html.Div(
    style={
        "minHeight": "100vh",       
        "padding": "16px",
        "backgroundColor": "#f5f5f5",
        "fontFamily": "Lato, sans-serif",
        "boxSizing": "border-box",
        "overflowY": "auto",       
    },
    children=[
        dcc.Store(id="leader-filter-store", data=None),
        dcc.Store(id="time-window-store", data=None),
        dcc.Store(id="highlight-mode-store", data=False),
        # Nav bar
        html.Div(
            style={
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "space-between",
                "marginBottom": "12px",
                "gap": "12px",
                "flexWrap": "wrap",  
            },
            children=[
                # Top left controls (tabs + chips)
                html.Div(
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "gap": "8px",
                        "flexWrap": "wrap",
                    },
                    children=[
                        # home tab button
                        html.Div(
                            id="tab-home",
                            style={
                                **TAB_BASE_STYLE,
                                "backgroundColor": "#333",   # active by default
                                "color": "#ffffff",          
                            },
                            children=[
                                html.Img(
                                    id="tab-home-icon",
                                    src="/assets/home-highlight.svg",
                                    style={**ICON_BASE_STYLE},
                                    alt="Home",
                                ),
                                html.Span(
                                    "Home Summary",
                                    id="tab-home-label",
                                    style={
                                        "fontSize": "16px",
                                        "fontWeight": "500",
                                        "whiteSpace": "nowrap",
                                    },
                                ),
                            ],
                        ),

                        # play tab button
                        html.Div(
                            id="tab-play",
                            style={
                                **TAB_BASE_STYLE,
                                "backgroundColor": "white",
                                "color": "#333333",         
                            },
                            children=[
                                html.Img(
                                    id="tab-play-icon",
                                    src="/assets/play.svg",
                                    style={**ICON_BASE_STYLE},
                                    alt="Play",
                                ),
                                html.Span(
                                    "Play Video",
                                    id="tab-play-label",
                                    style={
                                        "fontSize": "16px",
                                        "fontWeight": "500",
                                        "whiteSpace": "nowrap",
                                    },
                                ),
                            ],
                        ),

                        # PIT checkbox chip
                        html.Div(
                            id="pit-chip-container",
                            style={
                                "display": "flex",
                                "alignItems": "center",
                            },
                            children=dcc.Checklist(
                                id="pit-toggle",
                                options=[{"label": "Point-in-time views", "value": "pit"}],
                                value=[],  # default OFF
                                style={
                                    "display": "flex",
                                    "alignItems": "center",
                                },
                                inputStyle={"marginRight": "6px",
                                            "alignSelf": "center"},
                                labelStyle={
                                    "display": "flex",     
                                    "alignItems": "center",
                                    "padding": "6px 10px",
                                    "border": "1px solid #ccc",
                                    "borderRadius": "16px",
                                    "fontSize": "14px",
                                    "cursor": "pointer",
                                },
                            ),
                        ),

                    ],
                ),
                # Right aligned file name
                html.Div(
                    "Dyad T123",
                    style={
                        "fontWeight": "bold",
                        "fontSize": "14px",
                        "marginRight": "4px",
                        "flexShrink": 0,
                    },
                ),
            ],
        ),

        html.Div(
            id="page-content",
            children=home_layout(show_pit=False),   # default view is Home
        ),
    ],
)

@app.callback(
    Output("page-content", "children"),
    Output("tab-home", "style"),
    Output("tab-play", "style"),
    Output("tab-home-icon", "src"),
    Output("tab-play-icon", "src"),
    Output("pit-chip-container", "style"),  
    Input("tab-home", "n_clicks"),
    Input("tab-play", "n_clicks"),
    Input("pit-toggle", "value"),
)
def switch_tab(home_clicks, play_clicks, pit_value):
    home_clicks = home_clicks or 0
    play_clicks = play_clicks or 0

    show_pit = "pit" in (pit_value or [])

    active_tab_extra = {
        "backgroundColor": "#333",
        "color": "#ffffff",      
    }
    inactive_tab_extra = {
        "backgroundColor": "white",
        "color": "#333333",     
    }

    pit_style = {
        "display": "flex",
        "alignItems": "center",
    }
    if play_clicks > home_clicks:
        # play active
        home_style = {**TAB_BASE_STYLE, **inactive_tab_extra}
        play_style = {**TAB_BASE_STYLE, **active_tab_extra}
        home_icon_src = "/assets/home.svg"
        play_icon_src = "/assets/play-highlight.svg"
        content = play_layout()

        # hide PIT chip on Play page
        pit_style = {**pit_style, "display": "none"}
    else:
        # home active (default)
        home_style = {**TAB_BASE_STYLE, **active_tab_extra}
        play_style = {**TAB_BASE_STYLE, **inactive_tab_extra}
        home_icon_src = "/assets/home-highlight.svg"
        play_icon_src = "/assets/play.svg"
        content = home_layout(show_pit=show_pit)
        # pit_style stays visible on Home

    return content, home_style, play_style, home_icon_src, play_icon_src, pit_style

@app.callback(
    Output("play-heatmap-stack", "figure"),
    Input("video-player", "currentTime"),
)
def update_heatmaps_cursor(current_time):
    if current_time is None:
        raise PreventUpdate

    # round to whole seconds
    rounded_sec = int(round(current_time))

    # only update when the second actually changes
    last_sec = getattr(update_heatmaps_cursor, "last_sec", None)
    if rounded_sec == last_sec:
        # skip doing any work
        raise PreventUpdate

    # remember this second for next time
    update_heatmaps_cursor.last_sec = rounded_sec

    # map rounded_sec to absolute timestamp
    cursor_time = VIDEO_START + pd.to_timedelta(rounded_sec, unit="s")

    # start from base figure and add cursor line
    fig = go.Figure(BASE_PLAY_HEATMAP)
    fig.update_layout(
        shapes=[
            dict(
                type="line",
                x0=cursor_time,
                x1=cursor_time,
                y0=0,
                y1=1,
                xref="x",
                yref="paper",
                line=dict(color="black", width=3),
            )
        ]
    )

    return fig

@app.callback(
    Output("leading-behaviors", "figure"),
    Output("synchrony-violin", "figure"),
    Output("engagement-pie-chart", "figure"),
    Output("leader-filter-store", "data"),
    Input("leading-behaviors", "selectedData"),
    Input("time-window-store", "data"),
    State("leader-filter-store", "data"),
)
def filter_by_leader(selected_data, time_window, current_filter): 
    base_df = df.copy()

    full_bar_fig = make_synch_bar(base_df.copy())
    full_bar_fig.update_layout(clickmode="event+select")

    new_filter = None

    # leader selection from bar chart
    if selected_data and "points" in selected_data and selected_data["points"]:
        point = selected_data["points"][0]
        leader_label = point.get("x")  # "Child" / "Parent"
        if leader_label == "Child":
            new_filter = "Child"
        elif leader_label == "Parent":
            new_filter = "Parent"
    # else stays none

    filtered_df = base_df

    # leader filter
    if new_filter in ["Child", "Parent"]:
        code = "C" if new_filter == "Child" else "P"
        lead_col_norm = filtered_df[LEAD_COL].astype(str).str.strip()
        filtered_df = filtered_df[lead_col_norm.str.startswith(code)]

    # time-window filter
    if time_window and isinstance(time_window, dict):
        start = time_window.get("start")
        end = time_window.get("end")
        if start and end:
            start_ts = pd.to_datetime(start)
            end_ts = pd.to_datetime(end)
            ts_series = pd.to_datetime(filtered_df[TS_COL])
            mask = (ts_series >= start_ts) & (ts_series <= end_ts)
            filtered_df = filtered_df[mask]

    filtered_df = filtered_df.reset_index(drop=True)

    # style the bar chart to show which leader is active
    leading_fig = full_bar_fig
    if new_filter in ["Child", "Parent"]:
        selected = new_filter
        for trace in leading_fig.data:
            if getattr(trace, "name", None) == selected:
                trace.update(marker=dict(opacity=1.0))
            else:
                trace.update(marker=dict(opacity=0.25))
        leading_fig.update_layout(
            title=f"Synchronous Moments Led by Each Participant ({selected} leading only)"
        )
    else:
        for trace in leading_fig.data:
            trace.update(marker=dict(opacity=1.0))
        leading_fig.update_layout(title="Synchronous Moments Led by Each Participant")

    # violin + pie on filtered_df 
    violin_fig = make_violin(filtered_df.copy())
    pie_fig = make_pie(filtered_df.copy())

    return leading_fig, violin_fig, pie_fig, new_filter

@app.callback(
    Output("synch-glyph-play", "figure"),
    Input("video-player", "currentTime"),
)
def update_glyph_from_video(current_time):
    if current_time is None:
        current_time = 0.0

    # Map video time (seconds) to absolute timestamp
    cursor_time = VIDEO_START + pd.to_timedelta(current_time, unit="s")

    # Find the two nearest rows in df around that time
    pos = TS_SERIES.searchsorted(cursor_time)

    # the last point before the cursor (t0)
    # the next point after the cursor (t1)
    if pos <= 0: 
        i0 = i1 = 0
    elif pos >= len(TS_SERIES): 
        i0 = i1 = len(TS_SERIES) - 1
    else:   # we're in range
        i0 = pos - 1
        i1 = pos

    # get time intervals
    t0 = TS_SERIES.iloc[i0]
    t1 = TS_SERIES.iloc[i1]

    # get LF/HF values at the ends
    lf0 = float(df.loc[i0, LF_COL])
    lf1 = float(df.loc[i1, LF_COL])
    hf0 = float(df.loc[i0, HF_COL])
    hf1 = float(df.loc[i1, HF_COL])

    # Compute how far between t0 and t1 we are (from 0 to 1) using linear interpolation
    if t0 == t1:
        alpha = 0.0
    else:
        alpha = (cursor_time - t0) / (t1 - t0)

    # Sticky transitioning: hold value most of the time, move quickly in the middle
    if alpha <= 0.3:
        alpha = 0.0            # stick at previous second's value
    elif alpha >= 0.7:
        alpha = 1.0            # stick at next second's value
    else:
        # rescale from 0.3 to 0.7 instead of 0 to 1
        alpha = (alpha - 0.3) / (0.7 - 0.3)

    # get weighted average between:
        # lf0, hf0 (coherence at t0)
        # lf1, hf1 (coherence at t1)
        # alpha
    lf = (1.0 - alpha) * lf0 + alpha * lf1
    hf = (1.0 - alpha) * hf0 + alpha * hf1

    # get segment values/colors for this instant
    lf_vals, lf_cols = half_donut_segments(lf)
    hf_vals, hf_cols = half_donut_segments(hf)

    # start from the original glyph
    fig = go.Figure(FIG_SYNCH_GLYPH)

    # traces:
    # 0 = left background
    # 1 = right background
    # 2 = LF gradient arc
    # 3 = HF gradient arc
    fig.data[2].values = lf_vals
    fig.data[2].marker.colors = lf_cols

    fig.data[3].values = hf_vals
    fig.data[3].marker.colors = hf_cols

    fig.update_layout(
        transition=dict(
            duration=80,        
            easing="cubic-in-out",
        )
    )

    return fig

@app.callback(
    Output("behavior-play-img", "src"),
    Output("behavior-play-img", "title"),
    Output("leader-play-img", "src"),
    Input("video-player", "currentTime"),
)
def update_dyad_from_video(current_time):
    if current_time is None:
        current_time = 0.0

    idx = int(current_time)

    if idx < 0:
        idx = 0
    elif idx >= len(df):
        idx = len(df) - 1

    row = df.iloc[idx]

    # cje / sje are 1 when that engagement type is present, otherwise null
    cje_val = row.get("cje", 0)
    sje_val = row.get("sje", 0)

    cje_val = int(cje_val) if pd.notna(cje_val) else 0
    sje_val = int(sje_val) if pd.notna(sje_val) else 0

    if cje_val == 1:
        behav_src = "/assets/behav_CJE.png"
        behav_title = "Coordinated Joint Engagement (CJE) is a more advanced stage where the child actively participates by sharing attention with the caregiver and the object often shown by altering their gaze back and forth."
    elif sje_val == 1:
        behav_src = "/assets/behav_SJE.png"
        behav_title = "Supported Joint Engagement (SJE) is a state where a child and a caregiver are both actively involved with the same object or event, but the child is not yet actively acknowledging or responding to the caregiver's participation."
    else:
        behav_src = "/assets/behav_NoJE.png"
        behav_title = "No Joint Engagement is the absence of shared focus, where a child is either focused solely on an object (object engagement) or solely on a person (person engagement), or is otherwise uninvolved."

    lead_val = row.get(LEAD_COL, "")
    lead_str = str(lead_val).strip().upper()

    # If leading == "C", child; otherwise parent
    if lead_str.startswith("C"):
        leader_src = "/assets/lead_child.png"
    else:
        leader_src = "/assets/lead_parent.png"

    return behav_src, behav_title, leader_src

@app.callback(
    Output("timeline-heatmap", "figure"),
    Output("synch-glyph", "figure"),
    Output("dyad-leading-panel", "children"),
    Output("dyad-behavior-panel", "children"),
    Output("time-window-store", "data"),
    Output("highlight-mode-store", "data"),
    Input("timeline-heatmap", "clickData"),
    Input("timeline-heatmap", "hoverData"),
    State("highlight-mode-store", "data"),
    State("timeline-heatmap", "figure"),   
)
def nav_from_heatmap_click_or_hover(clickData, hoverData, highlight_mode, current_fig):

    # start from whatever is currently rendered in the layout
    if current_fig is not None:
        hm_fig = go.Figure(current_fig)
    else:
        hm_fig = (
            make_stacked_heatmaps(minimal=False)
            .update_xaxes(domain=[0.05, 1.0])
            .update_layout(margin=dict(l=90, r=20, t=0, b=0))
        )

    # defaults
    glyph_fig = FIG_SYNCH_GLYPH
    leading_panel = FIG_LEADING_PANEL
    behavior_panel = FIG_BEHAVIOR_PANEL
    window_payload = None

    # consider highlight ON if the store says so OR if the figure already
    # has shapes is the PIT-on default band + cursor
    has_shapes = bool(getattr(hm_fig.layout, "shapes", []))
    mode = bool(highlight_mode) or has_shapes

    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate

    trigger_prop = ctx.triggered[0]["prop_id"]  

    # click: toggles mode on/off and centers band on click
    if trigger_prop == "timeline-heatmap.clickData":
        if not clickData or "points" not in clickData or not clickData["points"]:
            return hm_fig, glyph_fig, leading_panel, behavior_panel, window_payload, mode

        # toggle mode
        mode = not mode

        # turning off: clear highlight & reset panels
        if not mode:
            base_fig = (
                make_stacked_heatmaps(minimal=False)
                .update_xaxes(domain=[0.05, 1.0])
                .update_layout(margin=dict(l=90, r=20, t=0, b=0))
            )
            return (
                base_fig,
                FIG_SYNCH_GLYPH,
                FIG_LEADING_PANEL,
                FIG_BEHAVIOR_PANEL,
                None,
                mode,
            )

        # turning on: use this click as cursor position
        x_val = clickData["points"][0]["x"]

    # hover: only active when mode is on
    elif trigger_prop == "timeline-heatmap.hoverData":
        if not mode:
            # highlight mode is off, ignore hover
            return hm_fig, glyph_fig, leading_panel, behavior_panel, window_payload, mode

        if not hoverData or "points" not in hoverData or not hoverData["points"]:
            raise PreventUpdate

        x_val = hoverData["points"][0]["x"]

    else:
        # any other case, just return current
        return hm_fig, glyph_fig, leading_panel, behavior_panel, window_payload, mode

    clicked_time = pd.to_datetime(x_val)

    # find nearest index in TS_SERIES
    pos = TS_SERIES.searchsorted(clicked_time)
    if pos <= 0:
        idx = 0
    elif pos >= len(TS_SERIES):
        idx = len(TS_SERIES) - 1
    else:
        before = TS_SERIES.iloc[pos - 1]
        after = TS_SERIES.iloc[pos]
        idx = pos - 1 if (clicked_time - before) <= (after - clicked_time) else pos

    cursor_time = TS_SERIES.iloc[idx]
    lf = float(df.loc[idx, LF_COL])
    hf = float(df.loc[idx, HF_COL])

    # 30-second window
    half_window = pd.Timedelta(seconds=30)
    window_start = max(TS_SERIES.iloc[0], cursor_time - half_window)
    window_end = min(TS_SERIES.iloc[-1], cursor_time + half_window)

    # update PIT glyph
    lf_vals, lf_cols = half_donut_segments(lf)
    hf_vals, hf_cols = half_donut_segments(hf)

    glyph_fig = go.Figure(FIG_SYNCH_GLYPH)
    glyph_fig.data[2].values = lf_vals
    glyph_fig.data[2].marker.colors = lf_cols
    glyph_fig.data[3].values = hf_vals
    glyph_fig.data[3].marker.colors = hf_cols
    glyph_fig.update_layout(
        transition=dict(duration=80, easing="cubic-in-out")
    )

    # highlight band + cursor line on heatmap
    hm_fig.update_layout(
        shapes=[
            dict(
                type="rect",
                x0=window_start,
                x1=window_end,
                y0=0,
                y1=1,
                xref="x",
                yref="paper",
                fillcolor="rgba(255, 230, 128, 0.35)",
                line=dict(color="rgba(255, 196, 0, 0.9)", width=1),
                layer="above",
            ),
            dict(
                type="line",
                x0=cursor_time,
                x1=cursor_time,
                y0=0,
                y1=1,
                xref="x",
                yref="paper",
                line=dict(color="black", width=3),
            ),
        ]
    )

    # dyad panels at this instant
    leading_panel = make_leading_panel(df, row_index=idx)
    behavior_panel = make_behavior_panel(df, row_index=idx)

    window_payload = {
        "start": window_start.isoformat(),
        "end": window_end.isoformat(),
    }

    return hm_fig, glyph_fig, leading_panel, behavior_panel, window_payload, mode

#Tooltip callbacks
@app.callback(
    Output({"type": "info-tooltip", "index": MATCH}, "style"),
    Input({"type": "info-icon", "index": MATCH}, "n_clicks"),
    State({"type": "info-tooltip", "index": MATCH}, "style"),
)
def toggle_info_tooltip(n_clicks, style):
    if not n_clicks:
        raise PreventUpdate

    style = style or {}
    current_display = style.get("display", "none")
    style["display"] = "none" if current_display == "block" else "block"
    return style


if __name__ == "__main__":
    app.run(debug=True)
