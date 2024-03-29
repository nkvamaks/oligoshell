from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory
from django.contrib.auth.models import User
import datetime

from . import models
from . import validators


class SequenceForm(forms.ModelForm):
    seq_name = forms.CharField(validators=[validators.validate_seq_name_regex])
    sequence = forms.CharField(validators=[validators.validate_seq])

    class Meta:
        model = models.Sequence
        fields = ['seq_name', 'sequence', 'scale', 'format_requested', 'purification_requested', 'order']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['seq_name'].widget.attrs.update({'class': 'form-control form-control-sm'})
        self.fields['sequence'].widget.attrs.update({'class': 'form-control form-control-sm'})
        self.fields['scale'].widget.attrs.update({'class': 'form-select form-select-sm'})
        self.fields['format_requested'].widget.attrs.update({'class': 'form-select form-select-sm'})
        self.fields['purification_requested'].widget.attrs.update({'class': 'form-select form-select-sm'})
        self.fields['order'].widget.attrs.update({'class': 'form-select form-select-sm'})


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
                                        can_order=False,
                                        )

class OrderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields['customer'].initial = (self.request.user.first_name + ' ' +
                                           self.request.user.last_name + ' ' +
                                           '(' + self.request.user.username + ')' )
        self.fields['email'].initial = self.request.user.email
        kwargs['request'] = self.request

    class Meta:
        model = models.Order
        fields = ['customer', 'email', 'comments', 'bulk_seqs']
        widgets = {'comments': forms.Textarea(attrs={'placeholder': 'Leave Your Comments About Order Here',
                                                     'rows': 1,
                                                     'class': 'form-control form-control-sm', }),
                   'bulk_seqs': forms.FileInput(attrs={'placeholder': 'Upload Bulk Sequences here in .csv Format',
                                                       'class': 'form-control form-control-sm'}),
                   }


class CustomModelChoiceIterator(forms.models.ModelChoiceIterator):
    def choice(self, obj):
        return (self.field.prepare_value(obj),
                self.field.label_from_instance(obj),
                obj)


class CustomModelChoiceField(forms.models.ModelMultipleChoiceField):
    def _get_choices(self):
        if hasattr(self, '_choices'):
            return self._choices
        return CustomModelChoiceIterator(self)
    choices = property(_get_choices,
                       forms.MultipleChoiceField._set_choices)

    def label_from_instance(self, seq):
        return seq.seq_name + ', ' + seq.sequence + ', ' + seq.scale + ', ' + seq.order.customer


class BatchForm(forms.ModelForm):

    class Meta:
        model = models.Batch
        fields = ['title', 'sequences2synthesis', 'comments']
        widgets = {'title': forms.TextInput(attrs={'class': 'form-control', 'value': datetime.date.today}),
                   'comments': forms.Textarea(attrs={'class': 'form-control',
                                                     'placeholder': 'Leave Your Comments Here',
                                                     'rows': 4}), }

    sequences2synthesis = CustomModelChoiceField(
        queryset=models.Sequence.objects.filter(synthesized=False),
        widget=forms.CheckboxSelectMultiple,
        label='Sequences Available for Synthesis',
    )

class PurificationForm(forms.ModelForm):
    class Meta:
        model = models.Purification
        fields = ('title', 'pur_method', 'pur_seqs', 'comments')
        widgets = {'title': forms.TextInput(attrs={'value': datetime.date.today,
                                                   'class': 'form-control'}),
                   'pur_method': forms.Select(attrs={'class': 'form-select'}),
                   'comments': forms.Textarea(attrs={'placeholder': 'Leave Your Comments Here',
                                                     'rows': 4,
                                                     'class': 'form-control' }), }

    pur_seqs = CustomModelChoiceField(
        queryset=models.Sequence.objects.filter(synthesized=True, complete=False, fail=False),
        widget=forms.CheckboxSelectMultiple,
        label='Sequences Available for Purification',
    )


class ConcentrationForm(forms.ModelForm):
    class Meta:
        model = models.Sequence
        fields = ('absorbance260', 'dilution_factor', 'volume', 'complete', 'fail')
        widgets = {'absorbance260': forms.NumberInput(attrs={'class': 'form-control form-control-sm'}),
                   'dilution_factor': forms.NumberInput(attrs={'class': 'form-control form-control-sm',
                                                             'value': 100}),
                   'volume': forms.NumberInput(attrs={'class': 'form-control form-control-sm'}),
                   'complete': forms.CheckboxInput(attrs={'class': 'form-check-input',
                                                          'value': models.Sequence.complete}),
                   'fail': forms.CheckboxInput(attrs={'class': 'form-check-input',
                                                      'value': models.Sequence.fail}),
                   }

class OrderCommentsForm(forms.ModelForm):
    class Meta:
        model = models.Order
        fields = ('comments',)
        widgets = {'comments': forms.Textarea(attrs={'value': models.Order.comments,
                                                     'rows': 4,
                                                     'class': 'form-control'}), }

class BatchCommentsForm(forms.ModelForm):
    class Meta:
        model = models.Batch
        fields = ('comments',)
        widgets = {'comments': forms.Textarea(attrs={'value': models.Batch.comments,
                                                     'rows': 4,
                                                     'class': 'form-control'}), }

class PurificationCommentsForm(forms.ModelForm):
    class Meta:
        model = models.Purification
        fields = ('comments',)
        widgets = {'comments': forms.Textarea(attrs={'value': models.Purification.comments,
                                                     'rows': 4,
                                                     'class': 'form-control'}), }


class CalcForm(forms.ModelForm):
    class Meta:
        model = models.Sequence
        fields = ('sequence', 'absorbance260', 'dilution_factor', 'volume')
        widgets = {'sequence': forms.Textarea(attrs={'rows': 3,
                                                     'class': 'form-control'}),
                   'absorbance260': forms.NumberInput(attrs={'class': 'form-control form-control-sm'}),
                   'dilution_factor': forms.NumberInput(attrs={'class': 'form-control form-control-sm'}),
                   'volume': forms.NumberInput(attrs={'class': 'form-control form-control-sm'}),
                   }



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