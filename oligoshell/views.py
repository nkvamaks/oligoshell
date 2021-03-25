from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from extra_views import CreateWithInlinesView, UpdateWithInlinesView
from extra_views import InlineFormSetFactory
from django.db import IntegrityError
from django.core.exceptions import ValidationError


from django.http import HttpResponseRedirect
from django.contrib import messages


from . import models
from . import forms
from . import validators


class IndexListView(LoginRequiredMixin, ListView):
    queryset = models.Sequence.objects.all()
    context_object_name = 'sequences'
    template_name = 'oligoshell/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders'] = models.Order.objects.all()
        context['batches'] = models.Batch.objects.all()
        return context


class SequenceUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Sequence
    template_name = 'oligoshell/sequence_detail.html'
    form_class = forms.ConcentrationForm

    def get_success_url(self):
        return reverse('oligoshell:sequence_detail', kwargs={'pk': self.object.id})


class SequenceCreateView(LoginRequiredMixin, CreateView):
    model = models.Sequence
    template_name = 'oligoshell/sequence_create.html'
    form_class = forms.SequenceForm
    success_url = reverse_lazy('oligoshell:index')


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = models.Order


# class SequenceInline(InlineFormSetFactory):
#     model = models.Sequence
#     fields = ['seq_name', 'sequence', 'scale', 'appearance_requested', 'purification_requested', ]
#     factory_kwargs = {'extra': 1, 'max_num': None, 'can_delete': False}


# class OrderCreateView(LoginRequiredMixin, CreateWithInlinesView):
#     model = models.Order
#     form_class = forms.OrderForm
#     inlines = [SequenceInline]
#     template_name = 'oligoshell/order_create.html'
#
#
#     def get_success_url(self):
#         return self.object.get_absolute_url()

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['orders'] = models.Order.objects.all()
    #     # context['batches'] = models.Batch.objects.all()
    #     return context


@login_required
def order_create(request):
    template_name = 'oligoshell/order_create.html'
    if request.method == 'GET':
        order_form = forms.OrderForm(request.GET or None)
        formset = forms.SequenceFormset(queryset=models.Sequence.objects.none())
    elif request.method == 'POST':
        order_form = forms.OrderForm(request.POST)
        formset = forms.SequenceFormset(request.POST)
        # if formset.is_valid():
        #     cd = formset.cleaned_data
        #     if len(set([x['seq_name'] for x in cd])) < len(cd):
        #         raise ValidationError('UUUUUUUUUUUUUUUUUUUUUUU')
        #
        # print(formset.cleaned_data)
        if order_form.is_valid() and formset.is_valid():
            order = order_form.save()
            for form in formset:
                validators.validate_sequence_regex(form.instance.sequence)
                #
                # if form.cleaned_data.get('seq_name') and form.cleaned_data.get('sequence'):
                #     seq = form.save(commit=False)
                #     seq.order = order
                #     seq.save()
                        # raise ValidationError('Lalala')
            # return render(request,
            #               template_name,
            #               {'form': order_form, 'formset': formset})
            return redirect(models.Sequence())
    return render(request, template_name, {'form': order_form, 'formset': formset})


class BatchCreateView(LoginRequiredMixin, CreateView):
    template_name = 'oligoshell/batch_create.html'
    form_class = forms.BatchForm
    success_url = reverse_lazy('oligoshell:batch')


class PurificationCreateView(LoginRequiredMixin, CreateView):
    template_name = 'oligoshell/purification_create.html'
    form_class = forms.PurificationForm
    success_url = reverse_lazy('oligoshell:index')


@login_required
def view_profile(request):
    return render(request, 'oligoshell/profile.html', {'user': request.user})


@login_required
def all_batches(request):
    batches = models.Batch.objects.all()
    return render(request,
                  'oligoshell/batch.html',
                  {"batches": batches})


@login_required
def batch_details(request, pk):
    batch = get_object_or_404(models.Batch, pk=pk)
    batches = models.Batch.objects.all()
    return render(request,
                  'oligoshell/batch_detail.html',
                  {'batch': batch,
                   'batches': batches})
