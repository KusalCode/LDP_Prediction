from mongoengine import Document, IntField, FloatField, ListField


class LiveResult(Document):
    time_stamp = IntField(required=True)
    input = ListField(FloatField(required=True))
    LDP_prediction = IntField(required=True)
