from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from django.forms import modelformset_factory

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


class OrderForm(forms.ModelForm):
    class Meta:
        model = models.Order
        fields = 'customer', 'email', 'comments'
        widgets = {'customer': forms.TextInput(attrs={'placeholder': 'John Smith'}),
                   'email': forms.EmailInput(attrs={'placeholder': 'John.Smith@fbi.com'}),
                   'comments': forms.Textarea(attrs={'placeholder': 'Leave Your Comments Here', 'rows': 3}), }

    # def clean(self):
    #     cleaned_data = self.cleaned_data
    #     print(cleaned_data)
    #     # seq_name = cleaned_data['seq_name']
    #     #
    #     # if seq_name and models.Sequence.objects.get(seq_name=seq_name):
    #     #     raise forms.ValidationError("not unique")
    #     #
    #     # # Always return the full collection of cleaned data.
    #     return cleaned_data


SequenceFormset = modelformset_factory(models.Sequence,
                                       fields=('seq_name',
                                               'sequence',
                                               'scale',
                                               'appearance_requested',
                                               'purification_requested'),
                                       extra=1)


class BatchForm(forms.ModelForm):
    class Meta:
        model = models.Batch
        fields = ('title', 'sequences2synthesis', 'notes')
        widgets = {'title': forms.TextInput(attrs={'placeholder': 'OLIG-15032021'}),
                   'notes': forms.Textarea(attrs={'placeholder': 'Leave Your Notes Here', 'rows': 3}), }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for myField in self.fields:
            self.fields[myField].widget.attrs['class'] = 'form-control'
        self.fields['sequences2synthesis'].widget = forms.widgets.CheckboxSelectMultiple()
        self.fields['sequences2synthesis'].queryset = models.Sequence.objects.filter(synthesized=False)


class PurificationForm(forms.ModelForm):
    class Meta:
        model = models.Purification
        fields = ('title', 'pur_seqs')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for myField in self.fields:
            self.fields[myField].widget.attrs['class'] = 'form-control'
        self.fields['pur_seqs'].widget = forms.widgets.CheckboxSelectMultiple()
        self.fields['pur_seqs'].queryset = models.Sequence.objects.filter(synthesized=True, done=False)
        self.helper = FormHelper()


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
