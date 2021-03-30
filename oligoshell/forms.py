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
    fields = ['seq_name', 'sequence', 'scale', 'appearance_requested', 'purification_requested', ]
    factory_kwargs = {'extra': 1, 'max_num': None, 'can_order': False, 'can_delete': False}
    # formset_kwargs = {'form_kwargs': {'initial': {'seq_name': 'example'}}}

    # def form_valid(self, form):
    #     form.instance.sequence = models.Sequence.objects.filter(seq_name=self.request.seq_name).order_by('sequence').last().sequence + 1
    #     return super().form_valid(form)


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
