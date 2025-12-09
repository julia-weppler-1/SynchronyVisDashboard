import pandas as pd
from dash import html


SJE_COL = "sje"
CJE_COL = "cje"

def get_behavior(df, row_index: int = 1):
    df_main = df.copy()
    for col in [SJE_COL, CJE_COL]:
        if col in df_main.columns:
            df_main[col] = pd.to_numeric(df_main[col], errors="coerce").fillna(0).astype(int)
    if len(df_main) == 0:
        return "No Joint Engagement", "/assets/behav_NoJE.png"

    idx = row_index # for now
    row = df_main.iloc[idx]

    cje_val = int(row.get(CJE_COL, 0) or 0)
    sje_val = int(row.get(SJE_COL, 0) or 0)

    # set picture based on value
    if cje_val == 1:
        return "Coordinated Joint Engagement", "/assets/behav_CJE.png"
    elif sje_val == 1:
        return "Supported Joint Engagement", "/assets/behav_SJE.png"
    else:
        return "No Joint Engagement", "/assets/behav_NoJE.png"


def make_behavior_panel(df, row_index: int = 1):

    label, img_src = get_behavior(df, row_index=row_index)

    # Set hover text based on engagement type
    if label == "Coordinated Joint Engagement":
        hover_text = "Coordinated Joint Engagement (CJE) is a more advanced stage where the child actively participates by sharing attention with the caregiver and the object often shown by altering their gaze back and forth."
    elif label == "Supported Joint Engagement":
        hover_text = "Supported Joint Engagement (SJE) is a state where a child and a caregiver are both actively involved with the same object or event, but the child is not yet actively acknowledging or responding to the caregiver's participation."
    else:
        hover_text = "No Joint Engagement is the absence of shared focus, where a child is either focused solely on an object (object engagement) or solely on a person (person engagement), or is otherwise uninvolved."


    # format img and panel container
    return html.Div(
        style={
            "display": "flex",
            "flexDirection": "column",
            "alignItems": "center",
            "justifyContent": "center",
            "height": "100%",
            "background": "rgba(0,0,0,0)"
        },
        children=[
            html.Img(
                src=img_src,
                alt=label,
                style={
                    "width": "100%",
                    "height": "auto",
                    "objectFit": "contain",
                    "borderRadius": "20px",
                },
            title=hover_text 
            ),
        ],
    )
