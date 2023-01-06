from decimal import Decimal

from django import forms


class RecordTimeField(forms.DecimalField):
    def to_python(self, value):
        minutes = value.split(':')[0]
        seconds = value.split(':')[1]
        return (Decimal(minutes) * 60) + Decimal(seconds)
