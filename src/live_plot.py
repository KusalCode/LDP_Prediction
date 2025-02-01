import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import threading
from collections import deque


X = deque(maxlen=20)
Y_pred = deque(maxlen=20)
Y_actual = deque(maxlen=20)


app = dash.Dash(__name__)


app.layout = html.Div(
    [
        dcc.Graph(id="live-graph"),
        dcc.Interval(id="graph-update", interval=1000, n_intervals=0),
    ]
)


def update_data(time_value, pred_value, actual_value):
    X.append(time_value)
    Y_pred.append(pred_value)
    Y_actual.append(actual_value)


@app.callback(Output("live-graph", "figure"), [Input("graph-update", "n_intervals")])
def update_graph(n):
    return {
        "data": [
            go.Scatter(
                x=list(X),
                y=list(Y_pred),
                mode="lines+markers",
                name="Prediction",
                line=dict(color="blue"),
            ),
            go.Scatter(
                x=list(X),
                y=list(Y_actual),
                mode="lines+markers",
                name="Actual",
                line=dict(color="red"),
            ),
        ],
        "layout": go.Layout(
            title="Real-Time Prediction vs Actual Values",
            xaxis=dict(title="Time", range=[min(X), max(X)]),
            yaxis=dict(
                title="Value",
                range=[
                    min(min(Y_pred), min(Y_actual)) - 1,
                    max(max(Y_pred), max(Y_actual)) + 1,
                ],
            ),
            template="plotly_dark",
        ),
    }


def start_dash_app():

    def run():
        app.run_server(debug=True, use_reloader=False)

    threading.Thread(target=run, daemon=True).start()
