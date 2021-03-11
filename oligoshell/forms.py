from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from extra_views import InlineFormSetFactory

from . import models


class SequenceForm(forms.ModelForm):
    class Meta:
        model = models.Sequence
        fields = ('seq_name',
                  'sequence',
                  'scale',
                  'appearance_requested',
                  'purification_requested',
                  'order')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for myField in self.fields:
            self.fields[myField].widget.attrs['class'] = 'form-control'
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('seq_name', css_class='form-group col-md-4 mb-2'),
                Column('sequence', css_class='form-group col-md-8 mb-2'),
                css_class='form-row'
            ),
            Row(
                Column('scale', css_class='form-group col-md-3 mb-0'),
                Column('appearance_requested', css_class='form-group col-md-3 mb-0'),
                Column('purification_requested', css_class='form-group col-md-3 mb-0'),
                Column('order', css_class='form-group col-md-3 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Add a new Sequence')
        )


class SequenceInline(InlineFormSetFactory):
    model = models.Sequence
    fields = ['seq_name', 'sequence', 'scale', 'appearance_requested', 'purification_requested']
    factory_kwargs = {'extra': 1, 'max_num': None, 'can_delete': False}


class OrderForm(forms.ModelForm):
    class Meta:
        model = models.Order
        fields = 'customer', 'email', 'comments'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for myField in self.fields:
            self.fields[myField].widget.attrs['class'] = 'form-control'
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('customer', css_class='form-group col-md-6 mb-2'),
                Column('email', css_class='form-group col-md-6 mb-2'),
                css_class='form-row'
            ),
            'comments',
            Submit('submit', 'Create a new Order')
        )


class BatchForm(forms.ModelForm):
    class Meta:
        model = models.Batch
        fields = ('title', 'sequences2synthesis', 'notes')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for myField in self.fields:
            self.fields[myField].widget.attrs['class'] = 'form-control'
        self.fields['sequences2synthesis'].widget = forms.widgets.CheckboxSelectMultiple()
        self.fields['sequences2synthesis'].queryset = models.Sequence.objects.filter(synthesized=False)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('title', css_class='form-group col-md-4 mb-2'),
                Column('notes', css_class='form-group col-md-8 mb-2'),
                css_class='form-row'
            ),
            'sequences2synthesis',
            Submit('submit', 'Create Synthesis Batch')
            )


class PurificationForm(forms.ModelForm):
    class Meta:
        model = models.Purification
        fields = ('title', 'pur_seqs')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for myField in self.fields:
            self.fields[myField].widget.attrs['class'] = 'form-control'
        self.fields['pur_seqs'].widget = forms.widgets.CheckboxSelectMultiple()
        self.fields['pur_seqs'].queryset = models.Sequence.objects.all()
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('pur_seqs', css_class='form-group col-md-8 mb-2'),
                Column('title', css_class='form-group col-md-4 mb-2'),
                css_class='form-row'
            ),
            Submit('submit', 'Create Synthesis Batch')
            )


class ConcentrationForm(forms.ModelForm):
    class Meta:
        model = models.Sequence
        fields = ('absorbance260', 'volume')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for myField in self.fields:
            self.fields[myField].widget.attrs['class'] = 'form-control'
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'absorbance260',
            'volume',
            Submit('submit', 'Save Measurements')
        )
