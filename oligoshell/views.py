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
from django.http import HttpResponseRedirect
from django.contrib import messages


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

    # def post(self, request, *args, **kwargs):
    #     # super().post() maybe raise a ValidationError if it is failure to save
    #     response = super().post(request, *args, **kwargs)
    #     # the below code is optional. django has responsed another erorr message
    #     if not self.object:
    #         messages.info(request, 'UNIQUE constraint failed.')
    #     return response

    # def post(self, request, *args, **kwargs):
    #     """
    #     Handles POST requests, instantiating a form and formset instances with the
    #     passed POST variables and then checked for validity.
    #     """
    #     form_class = self.get_form_class()
    #     form = self.get_form(form_class)
    #
    #     initial_object = self.object
    #     if form.is_valid():
    #         self.object = form.save(commit=False)
    #         form_validated = True
    #     else:
    #         form_validated = False
    #
    #     inlines = self.construct_inlines()
    #
    #     if all_valid(inlines) and form_validated:
    #         return self.forms_valid(form, inlines)
    #     self.object = initial_object
    #     return self.forms_invalid(form, inlines)
    #
    # # PUT is a valid HTTP verb for creating (with a known URL) or editing an
    # # object, note that browsers only support POST for now.
    # def put(self, *args, **kwargs):
    #     return self.post(*args, **kwargs)

    # def get(self, request, *args, **kwargs):
    #     form = self.form_class(initial=self.initial)
    #     return render(request, self.template_name, {'form': form})

    # def post(self, request, *args, **kwargs):
    #     form = self.form_class(request.POST)
    #     if form.is_valid():
    #         print(form.cleaned_data)
    #     else:
    #         print(form.errors)
    #         # <process form cleaned data>
    #         return HttpResponseRedirect('index')
    #
    #     return render(request, self.template_name, {'form': form})


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
