from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from . import models
from . import forms


class IndexListView(LoginRequiredMixin, ListView):
    queryset = models.Sequence.objects.all()
    context_object_name = 'sequences'
    template_name = 'oligoshell/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexListView, self).get_context_data(**kwargs)
        context['orders'] = models.Order.objects.all()
        context['batches'] = models.Batch.objects.all()
        return context


class SequenceDetailView(LoginRequiredMixin, DetailView):
    model = models.Sequence


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = models.Order


class SequenceCreateView(LoginRequiredMixin, CreateView):
    model = models.Sequence
    template_name = 'oligoshell/sequence_create.html'
    form_class = forms.SequenceForm
    success_url = reverse_lazy('oligoshell:index')


class OrderCreateView(LoginRequiredMixin, CreateView):
    template_name = 'oligoshell/order_create.html'
    form_class = forms.OrderForm
    success_url = reverse_lazy('oligoshell:sequence_create')


class BatchCreateView(LoginRequiredMixin, CreateView):
    template_name = 'oligoshell/batch_create.html'
    form_class = forms.BatchForm
    success_url = reverse_lazy('oligoshell:index')


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
