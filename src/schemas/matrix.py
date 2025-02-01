from mongoengine import Document, IntField, FloatField


class Matrix(Document):
    time_stamp = IntField(required=True)
    mean_absolute_error = FloatField()
