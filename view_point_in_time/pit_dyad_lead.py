import pandas as pd
from dash import html


TS_COL = "timestamp"
LEADING_COL = "leading"


def get_leader(df, row_index: int = 1):

    if len(df) == 0:
        return "Child", "/assets/lead_child.png"

    idx = max(0, min(row_index, len(df) - 1))
    # get 'C' or 'P' from first row in leading col
    leader_val = str(df.iloc[idx].get(LEADING_COL, "")).strip().upper()
    if leader_val.startswith("P"):
        return "Parent", "/assets/lead_parent.png"
    else:
        return "Child", "/assets/lead_child.png"

def make_leading_panel(df, row_index: int = 1):

    leader_label, leader_img = get_leader(df, row_index=row_index)

    return html.Div(
        style={
            "display": "flex",
            "flexDirection": "column",
            "alignItems": "center",
            "justifyContent": "center",
            "maxWidth": "220px",
            "margin": "0 auto",
        },
        children=[
            html.Div(
                ["Leading", html.Br(), "Physiologic Synchrony"],
                style={
                    "fontWeight": "bold",
                    "fontSize": "13px",
                    "marginBottom": "8px",
                    "textAlign": "center",
                },
            ),
            html.Img(
                src=leader_img,
                alt=f"{leader_label} leading physiologic synchrony",
                style={
                    "width": "160px",
                    "height": "160px",
                    "objectFit": "contain",
                    "display": "block",
                },
            ),
        ],
    )
