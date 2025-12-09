import pandas as pd
import plotly.express as px
from dash import dcc
from load_data import df as main_df

df = main_df.copy()

fig = px.line(
    df,
    x="lf_coh",
    y="hf_coh",
    markers=True,
    title="Data over Index",
)

chart = dcc.Graph(id="my-chart", figure=fig)

