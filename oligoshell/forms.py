from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django.forms import BaseModelFormSet, BaseInlineFormSet, modelformset_factory, inlineformset_factory
from extra_views import InlineFormSetFactory
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS

from . import models
from . import validators


class SequenceForm(forms.ModelForm):
    seq_name = forms.CharField(validators=[validators.validate_seq_name_regex])

    sequence = forms.CharField(validators=[validators.validate_sequence_regex,
                                           validators.validate_modifications])

    class Meta:
        model = models.Sequence
        fields = ['seq_name', 'sequence', 'scale', 'appearance_requested', 'purification_requested']


class BaseSequenceFormSet(BaseInlineFormSet):

    def clean(self):
        seq_names = []
        for form in self.forms:
            if form.cleaned_data.get('seq_name') in seq_names:
                form.add_error('seq_name', 'The Name Already Exists')
            elif form.cleaned_data.get('seq_name'):
                seq_names.append(form.cleaned_data.get('seq_name'))


SequenceFormset = inlineformset_factory(models.Order, models.Sequence,
                                        form=SequenceForm,
                                        formset=BaseSequenceFormSet,
                                        extra=0,
                                        min_num=1,
                                        can_delete=False,
                                        can_order=False)


class OrderForm(forms.ModelForm):

    class Meta:
        model = models.Order
        fields = 'customer', 'email', 'comments'
        widgets = {'customer': forms.TextInput(attrs={'placeholder': 'John Smith'}),
                   'email': forms.EmailInput(attrs={'placeholder': 'John.Smith@fbi.com'}),
                   'comments': forms.Textarea(attrs={'placeholder': 'Leave Your Comments Here', 'rows': 3}), }


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
