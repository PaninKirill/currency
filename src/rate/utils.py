from datetime import datetime
from decimal import Decimal


def to_decimal(num) -> Decimal:
    return round(Decimal(num), 2)


def display(model_object, attr):
    display_attr = f'get_{attr}_display'

    if hasattr(model_object, display_attr):
        return getattr(model_object, display_attr)()

    if type(getattr(model_object, attr)) is datetime:
        return model_object.datetime_str()

    return getattr(model_object, attr)
