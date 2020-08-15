from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from . import models


# class OrderListView(LoginRequiredMixin, ListView):
#     queryset = models.Order.objects.all()
#     context_object_name = 'orders'
#     template_name = 'oligoshell/index.html'


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

# def sequence_detail(request, order_id, seq_id):
#     current_sequence = models.Sequence.objects.get(pk=seq_id)
#     current_order = models.Order.objects.get(pk=order_id)
#     context = {'current_sequence': current_sequence, 'current_order': current_order}
#     return render(request, 'oligoshell/sequence_detail.html', context)
#
#
# def order_detail(request, order_id):
#     sequences = models.Sequence.objects.filter(order=order_id)
#     orders = models.Order.objects.all()
#     current_order = models.Order.objects.get(pk=order_id)
#     context = {'sequences': sequences, 'orders': orders, 'current_order': current_order}
#     return render(request, 'oligoshell/order_detail.html', context)
