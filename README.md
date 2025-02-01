# LDP Prediction

## Project Overview

LDP Prediction is a machine learning project designed to predict the next number in the **Byner Analyzer Sequence** using a trained **LSTM (Long Short-Term Memory) neural network model**. The model is trained and saved using **TensorFlow/Keras**.

### Features
-  **Real-time visualization** of actual vs. predicted values.
-  **MongoDB integration** for storing historical predictions, real-time data, and mean squared error values.

---

##  Installation

Follow these steps to set up the project:

1. **Clone the repository:**
   ```sh
   git clone <repository_url>
   ```
2. **Navigate to the project directory:**
   ```sh
   cd LDP-Prediction
   ```
3. **Install the required dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

---

## Configuration (.env File)

Before running the project, update the **.env** file with your credentials and database information:
```ini
URI="your_mongoDB_URI"
DB_NAME="your_database_name"
API_TOKEN="your_deriv_API_account"
```

---

## Prerequisites

Ensure you have the following installed:
-  **Python 3.12 or later**
-  **MongoDB** (if using a local database or you can use cloud as well)
-  Required Python libraries (installed via `requirements.txt`)

---

## Usage

### Training the Model

To train the model, use the **`model_implementation.ipynb`** notebook. Once trained, the model will be saved to the **`model`** folder.

### Predicting the Next Number

To predict the next number in the sequence, run the following command:
```sh
python idp_predictor.py
```
#### This will:
 Load the trained model.
 Process input data.
 Generate the next predicted number in the Byner Analyzer Sequence.
 Display a real-time graph comparing actual vs. predicted values.
 Compute and display **Mean Absolute Error (MAE)** values.
 Save real-time data to MongoDB for further analysis.

---



