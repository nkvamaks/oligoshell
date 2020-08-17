from django.forms import ModelForm
from . import models


class SequenceForm(ModelForm):
    class Meta:
        model = models.Sequence
        fields = ('seq_name', 'sequence', 'scale', 'appearance_requested', 'order')


class OrderForm(ModelForm):
    class Meta:
        model = models.Order
        fields = ('customer', 'email', 'comments')
