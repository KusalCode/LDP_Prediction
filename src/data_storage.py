import os
import csv
from dotenv import load_dotenv
from mongoengine import connect
from mongoengine.connection import get_db

load_dotenv()

CSV_FILE_PATH = os.getenv("CSV_FILE_PATH")
URI = os.getenv("URI")
DB_NAME = os.getenv("DB_NAME")


def save_data_to_csv(data):
    # Combine data into rows
    rows = zip(data["timestamp"], data["price"], data["ldp"])

    # Write to CSV file
    with open(CSV_FILE_PATH, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Price", "LDP"])  # CSV headers
        writer.writerows(rows)

    print(f"Historical data saved to {CSV_FILE_PATH}")


def connect_to_mongo():
    try:
        connect(db=DB_NAME, host=URI, retryWrites=True, ssl=True)
        print("Connected to MongoDB Atlas successfully!")
        db_names = get_db().list_collection_names()
        return db_names
    except Exception as e:
        raise RuntimeError(f"Failed to connect to MongoDB: {e}")
