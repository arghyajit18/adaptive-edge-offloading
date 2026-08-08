import plotly.graph_objs as go
from dash import dcc, html


def metric_card(title: str, fig_id: str) -> html.Div:
    return html.Div(
        className="card",
        children=[
            html.H4(title, className="card-title"),
            dcc.Graph(
                id=fig_id,
                animate=True,
                config={"displayModeBar": False},
            ),
        ],
    )


def empty_figure(y_title: str) -> go.Figure:
    fig = go.Figure()
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=30, r=10, t=30, b=30),
        xaxis_title="Time (s)",
        yaxis_title=y_title,
        showlegend=False,
    )
    return fig
