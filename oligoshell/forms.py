from django import forms
from . import models


class SequenceForm(forms.ModelForm):
    class Meta:
        model = models.Sequence
        fields = ('seq_name', 'sequence', 'scale', 'appearance_requested', 'order')


class OrderForm(forms.ModelForm):
    class Meta:
        model = models.Order
        fields = ('customer', 'email', 'comments')
