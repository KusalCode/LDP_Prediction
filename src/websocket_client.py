import os
import websocket
import json
import threading
from dotenv import load_dotenv

load_dotenv()

# WebSocket URL and API token
API_TOKEN = os.getenv("API_TOKEN")
DERIV_API_URL = os.getenv("DERIV_API_URL")

hist_data = []
live_data = None
ws_instance = None  # Global variable to hold WebSocket instance


def on_message(ws, message):
    global hist_data, live_data
    data = json.loads(message)

    if "error" in data:
        print("Error:", data["error"]["message"])
        ws.close()
        return

    if "history" in data:
        hist_data.append(data)
        ws.received_count += len(data["history"]["times"])

        if ws.received_count < ws.total_count:
            earliest_timestamp = data["history"]["times"][0]
            fetch_more_data(ws, earliest_timestamp, ws.batch_size)
        else:
            print(f"Completed fetching {ws.received_count} historical data points.")
            ws.close()

    elif "tick" in data:
        live_data = data


def on_error(ws, error):
    print("Error:", error)


def on_open(ws, request_type, count, total_count=None):
    print("Connected to Deriv API")

    # Authorize with API token
    auth_request = {"authorize": API_TOKEN}
    ws.send(json.dumps(auth_request))

    ws.total_count = total_count or count
    ws.received_count = 0
    ws.batch_size = count

    if request_type == "history":
        fetch_more_data(ws, "latest", ws.batch_size)

    elif request_type == "live":
        live_tick_request = {"ticks": "R_100", "subscribe": 1}
        ws.send(json.dumps(live_tick_request))


def fetch_more_data(ws, end_time, count):
    """Request more historical data from the earliest timestamp"""
    remaining = ws.total_count - ws.received_count
    batch_size = min(remaining, count)

    if batch_size <= 0:
        print(f"Completed fetching {ws.received_count} historical data points.")
        ws.close()
        return

    history_request = {
        "ticks_history": "R_100",
        "end": end_time,
        "granularity": 60,
        "count": batch_size,
    }
    print(f"Requesting {batch_size} more data points until {end_time}...")
    ws.send(json.dumps(history_request))


def on_close(ws, close_status_code, close_msg):
    print("Disconnected from Deriv API")


def start_websocket(request_type, total_count=None):
    clear_data()
    global ws_instance

    if request_type not in ["history", "live"]:
        print("Invalid request type. Please use 'history' or 'live'.")
        return

    ws_instance = websocket.WebSocketApp(
        DERIV_API_URL,
        on_message=on_message,
        on_error=on_error,
        on_open=lambda ws: on_open(ws, request_type, 5000, total_count),
        on_close=on_close,
    )

    ws_instance.run_forever()


def stop_websocket():
    global ws_instance

    clear_data()

    if ws_instance:
        ws_instance.close()
        ws_instance = None
        print("WebSocket connection closed.")


def clear_data():
    global hist_data, live_data
    hist_data = []
    live_data = None
