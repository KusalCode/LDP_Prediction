from mongoengine import Document, IntField, FloatField, ListField


class TrainingData(Document):
    time_stamp = IntField(required=True)
    price = FloatField(required=True)
    LDP_prediction = IntField(required=True)
