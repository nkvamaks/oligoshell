from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy

from . import models
from . import forms


class IndexListView(LoginRequiredMixin, ListView):
    queryset = models.Sequence.objects.all()
    context_object_name = 'sequences'
    template_name = 'oligoshell/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexListView, self).get_context_data(**kwargs)
        context['orders'] = models.Order.objects.all()
        return context


class SequenceDetailView(LoginRequiredMixin, DetailView):
    model = models.Sequence


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = models.Order


class SequenceCreateView(CreateView):
    template_name = 'oligoshell/sequence_create.html'
    form_class = forms.SequenceForm
    success_url = reverse_lazy('oligoshell:index')

#    def get_context_data(self, **kwargs):
#        context = super().get_context_data(**kwargs)
#        context['orders'] = Order.objects.all()
#        return context


class OrderCreateView(CreateView):
    template_name = 'oligoshell/order_create.html'
    form_class = forms.OrderForm
    success_url = reverse_lazy('oligoshell:index')