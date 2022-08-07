from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django.forms import BaseInlineFormSet, inlineformset_factory
from django.contrib.auth.models import User
import datetime

from . import models
from . import validators


class SequenceForm(forms.ModelForm):
    seq_name = forms.CharField(validators=[validators.validate_seq_name_regex])

    sequence = forms.CharField(validators=[validators.validate_sequence_regex,
                                           validators.validate_modifications])

    class Meta:
        model = models.Sequence
        fields = ['seq_name', 'sequence', 'scale', 'format_requested', 'purification_requested']


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
        fields = ['customer', 'email', 'comments']
        widgets = {'customer': forms.TextInput(attrs={'value': str(
                                                        User.objects.get().first_name + ' ' +
                                                        User.objects.get().last_name + ' ' +
                                                        '(' + User.objects.get().username + ')')}),
                   'email': forms.EmailInput(attrs={'value': User.objects.get().email}),
                   'comments': forms.Textarea(attrs={'placeholder': 'Leave Your Comments Here', 'rows': 3}), }


class CustomSequences2synthesis(forms.ModelMultipleChoiceField):
    def label_from_instance(self, seq):
        return seq.seq_name + ', ' + seq.sequence + ', ' + seq.scale + ', ' + seq.order.customer


class CustomPurseqs(forms.ModelMultipleChoiceField):
    def label_from_instance(self, seq):
        return seq.seq_name + ', ' + seq.sequence + ', ' + seq.scale + ', ' + seq.order.customer


class BatchForm(forms.ModelForm):

    class Meta:
        model = models.Batch
        fields = ['title', 'sequences2synthesis', 'comments']
        widgets = {'title': forms.TextInput(attrs={'value': datetime.date.today}),
                   'comments': forms.Textarea(attrs={'placeholder': 'Leave Your Comments Here', 'rows': 2}), }

    sequences2synthesis = CustomSequences2synthesis(
        queryset=models.Sequence.objects.filter(synthesized=False),
        widget=forms.CheckboxSelectMultiple,
        label='Sequences Available for Synthesis',
    )

class PurificationForm(forms.ModelForm):
    class Meta:
        model = models.Purification
        fields = ('title', 'pur_method', 'pur_seqs', 'comments')
        widgets = {'title': forms.TextInput(attrs={'value': datetime.date.today}),
                   'comments': forms.Textarea(attrs={'placeholder': 'Leave Your Comments Here', 'rows': 2}), }

    pur_seqs = CustomPurseqs(
        queryset=models.Sequence.objects.filter(synthesized=True, done=False),
        widget=forms.CheckboxSelectMultiple,
        label='Sequences Available for Purification',
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


class UserRegistrationForm(forms.ModelForm):

    password = forms.CharField(label='Password',
                               widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password',
                                widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError("Passwords do not match!")
        return cd['password']