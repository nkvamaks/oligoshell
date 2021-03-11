from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from extra_views import CreateWithInlinesView, UpdateWithInlinesView


from . import models
from . import forms


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


class OrderCreateView(LoginRequiredMixin, CreateWithInlinesView):
    model = models.Order
    form_class = forms.OrderForm
    inlines = [forms.SequenceInline]
    template_name = 'oligoshell/order_create.html'

    def get_success_url(self):
        return self.object.get_absolute_url()


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
