import os
import threading

import numpy as np
from collections import deque
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler

from src.websocket_client import start_websocket, stop_websocket
from src import websocket_client

from src.schemas.live_results import LiveResult
from src.schemas.matrix import Matrix
from src.data_storage import connect_to_mongo

from src.live_plot import start_dash_app, update_data
import time


MODEL_DIR = "model"
sequence_length = 20

timepoint_list = deque(maxlen=sequence_length)
ldp_list = deque(maxlen=sequence_length)
predict_list = deque(maxlen=sequence_length)

stop_event = threading.Event()
model = load_model(os.path.join(MODEL_DIR, "model.keras"))


def predict_next(model, input, sequence_length):
    scaler = MinMaxScaler()
    input = np.array(input)
    scaled_input = scaler.fit_transform(input.reshape(-1, 1))
    prediction = model.predict(scaled_input.reshape((1, sequence_length, 1)), verbose=0)
    rescaled_prediction = scaler.inverse_transform(prediction)
    price = np.round(rescaled_prediction, 2)[0, 0]
    ldps = int("{:.2f}".format(price)[-1])
    return ldps


def get_error():
    mae = None
    print("Error calculation will start after storing enough data..")
    if len(predict_list) == sequence_length:
        active_target = np.array(ldp_list)[1:]
        pred_target = np.array(predict_list)[0:-1]
        mae = np.mean(np.abs(active_target - pred_target))
    return mae


def generate_sequence():
    stop_event.clear()

    # Fetch historical data
    start_websocket("history", sequence_length)
    hist_data = websocket_client.hist_data
    hist_time = hist_data[-1]["history"]["times"]
    hist_price = hist_data[-1]["history"]["prices"]
    hist_ldps = [int("{:.2f}".format(value)[-1]) for value in hist_price]
    timepoint_list.extend(hist_time)
    ldp_list.extend(hist_ldps)

    # Fetch live data
    def store_live_data():
        while not stop_event.is_set():
            if websocket_client.live_data:
                live_data = websocket_client.live_data
                live_time = live_data["tick"]["epoch"]
                live_price = live_data["tick"]["quote"]
                live_ldps = int("{:.2f}".format(live_price)[-1])

                if not live_time in timepoint_list:
                    timepoint_list.append(live_time)
                    ldp_list.append(live_ldps)

                    prediction = predict_next(model, ldp_list, sequence_length)
                    predict_list.append(prediction)

                    mae = get_error()
                    print(
                        "Time : ",
                        timepoint_list[-1],
                        " | Prediction : ",
                        prediction,
                        " | MAE : ",
                        mae,
                        "\n",
                    )

                    LiveResult(
                        time_stamp=timepoint_list[-1],
                        input=ldp_list,
                        LDP_prediction=prediction,
                    ).save()

                    update_data(live_time, prediction, live_ldps)

                    if mae:
                        mean_error = Matrix(
                            time_stamp=timepoint_list[1], mean_absolute_error=mae
                        )
                        mean_error.save()

            time.sleep(1)
        print("Data fetching stopped.")

    live_thread = threading.Thread(target=start_websocket, args=("live",))
    live_thread.start()

    data_thread = threading.Thread(target=store_live_data)
    data_thread.start()


def stop_threads():
    stop_event.set()
    print("Stopping threads...")
    stop_websocket()


def main():

    db_names = connect_to_mongo()

    if "live_result" in db_names:
        LiveResult.drop_collection()
    elif "matrix" in db_names:
        Matrix.drop_collection()

    generate_sequence()
    print("********** Live Graph **********")
    start_dash_app()


if __name__ == "__main__":
    main()
