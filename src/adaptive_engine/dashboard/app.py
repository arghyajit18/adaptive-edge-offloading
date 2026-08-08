import os, time, sqlite3
from pathlib import Path
import dash
import pandas as pd
import plotly.graph_objs as go
from dash import Input, Output, dcc, html
from sqlalchemy.ext.asyncio import create_async_engine
from adaptive_engine.metrics.models import LinkMetric, DecisionLog, Base
from adaptive_engine.metrics.store import MetricsStore
from adaptive_engine.dashboard.components import metric_card, empty_figure
from adaptive_engine.config import settings

DB_URL = settings.db.url.replace("sqlite+aiosqlite:///", "sqlite:///")
sqlite_path = Path(DB_URL.replace("sqlite:///", ""))

app = dash.Dash(__name__, title="Adaptive Edge‑Offloading Dashboard")
server = app.server

app.layout = html.Div(
    className="container",
    children=[
        html.H2("🛸 Adaptive Edge‑Offloading Engine – Live Dashboard"),
        html.Div(className="row", children=[
            metric_card("Bandwidth (Mbps)", "fig-bw"),
            metric_card("RTT (ms)", "fig-rtt"),
            metric_card("Packet Loss", "fig-loss"),
            metric_card("SINR (dB)", "fig-sinr"),
        ]),
        html.Div(className="row", children=[
            metric_card("Decision Ratio (last 200)", "fig-dec-ratio"),
            metric_card("Predicted Latency (ms)", "fig-lat"),
            metric_card("Predicted Energy (mJ)", "fig-en"),
            metric_card("Deadline‑Miss Rate", "fig-miss"),
        ]),
        dcc.Store(id="last-link-ts", data=0),
        dcc.Store(id="last-dec-ts", data=0),
        dcc.Interval(id="tick", interval=settings.dashboard.refresh_interval_sec*1000, n_intervals=0),
    ],
)

def _fetch_link_metrics(since_ms: int) -> pd.DataFrame:
    q = f"""
        SELECT timestamp, bandwidth_mbps, rtt_ms, loss, sinr_db
        FROM link_metrics
        WHERE (strftime('%s', timestamp) * 1000) > {since_ms}
        ORDER BY timestamp
    """
    with sqlite3.connect(sqlite_path) as con:
        return pd.read_sql_query(q, con, parse_dates=["timestamp"])

def _fetch_decisions(since_ms: int) -> pd.DataFrame:
    q = f"""
        SELECT timestamp, decision, predicted_latency_ms, predicted_energy_mj, deadline_ms
        FROM decision_log
        WHERE (strftime('%s', timestamp) * 1000) > {since_ms}
        ORDER BY timestamp
    """
    with sqlite3.connect(sqlite_path) as con:
        return pd.read_sql_query(q, con, parse_dates=["timestamp"])

@app.callback(
    Output("fig-bw","figure"),
    Output("fig-rtt","figure"),
    Output("fig-loss","figure"),
    Output("fig-sinr","figure"),
    Output("last-link-ts","data"),
    Input("tick","n_intervals"),
    Input("last-link-ts","data"),
)
def update_network_graphs(_n, last_ts):
    df = _fetch_link_metrics(last_ts)
    if df.empty:
        return (empty_figure("Mbps"), empty_figure("ms"), empty_figure("Loss"),
                empty_figure("dB"), last_ts)
    new_ts = int(df["timestamp"].iloc[-1].timestamp()*1000)
    fig_bw = go.Figure(go.Scatter(x=df["timestamp"], y=df["bandwidth_mbps"], mode="lines+markers"))
    fig_bw.update_layout(template="plotly_white", yaxis_title="Mbps", margin=dict(l=30,r=10,t=30,b=30))
    fig_rtt = go.Figure(go.Scatter(x=df["timestamp"], y=df["rtt_ms"], mode="lines+markers"))
    fig_rtt.update_layout(template="plotly_white", yaxis_title="ms", margin=dict(l=30,r=10,t=30,b=30))
    fig_loss = go.Figure(go.Scatter(x=df["timestamp"], y=df["loss"], mode="lines+markers"))
    fig_loss.update_layout(template="plotly_white", yaxis_title="Loss", margin=dict(l=30,r=10,t=30,b=30))
    fig_sinr = go.Figure(go.Scatter(x=df["timestamp"], y=df["sinr_db"], mode="lines+markers"))
    fig_sinr.update_layout(template="plotly_white", yaxis_title="dB", margin=dict(l=30,r=10,t=30,b=30))
    return fig_bw, fig_rtt, fig_loss, fig_sinr, new_ts

@app.callback(
    Output("fig-dec-ratio","figure"),
    Output("fig-lat","figure"),
    Output("fig-en","figure"),
    Output("fig-miss","figure"),
    Output("last-dec-ts","data"),
    Input("tick","n_intervals"),
    Input("last-dec-ts","data"),
)
def update_decision_graphs(_n, last_ts):
    df = _fetch_decisions(last_ts)
    if df.empty:
        return (empty_figure("Ratio"), empty_figure("ms"), empty_figure("mJ"),
                empty_figure("Miss %"), last_ts)
    new_ts = int(df["timestamp"].iloc[-1].timestamp()*1000)
    recent = df.tail(200)
    ratio = recent["decision"].value_counts()
    fig_ratio = go.Figure(go.Pie(labels=ratio.index.tolist(), values=ratio.values.tolist(), hole=0.4))
    fig_ratio.update_layout(template="plotly_white", margin=dict(l=10,r=10,t=30,b=10))
    fig_lat = go.Figure(go.Scatter(x=recent["timestamp"], y=recent["predicted_latency_ms"], mode="lines+markers"))
    fig_lat.update_layout(template="plotly_white", yaxis_title="ms", margin=dict(l=30,r=10,t=30,b=30))
    fig_en = go.Figure(go.Scatter(x=recent["timestamp"], y=recent["predicted_energy_mj"], mode="lines+markers"))
    fig_en.update_layout(template="plotly_white", yaxis_title="mJ", margin=dict(l=30,r=10,t=30,b=30))
    recent["miss"] = recent["predicted_latency_ms"] > recent["deadline_ms"]
    miss_rate = recent["miss"].rolling(50).mean()*100
    fig_miss = go.Figure(go.Scatter(x=recent["timestamp"], y=miss_rate, mode="lines"))
    fig_miss.update_layout(template="plotly_white", yaxis_title="% Miss", margin=dict(l=30,r=10,t=30,b=30))
    return fig_ratio, fig_lat, fig_en, fig_miss, new_ts

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
