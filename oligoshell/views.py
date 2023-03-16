from django.views.generic import ListView
#from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.views.generic.edit import CreateView
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.db.models import Q

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
        context['purifications'] = models.Purification.objects.all()
        return context


class SequenceUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Sequence
    template_name = 'oligoshell/sequence_detail.html'
    form_class = forms.ConcentrationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders'] = models.Order.objects.all()
        context['batches'] = models.Batch.objects.all()
        context['purifications'] = models.Purification.objects.all()
        return context

    def get_success_url(self):
        return reverse('oligoshell:sequence_detail', kwargs={'pk': self.object.id})


class SequenceCreateView(LoginRequiredMixin, CreateView):
    model = models.Sequence
    form_class = forms.SequenceForm
    template_name = 'oligoshell/sequence_create.html'
    success_url = reverse_lazy('oligoshell:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders'] = models.Order.objects.all()
        context['batches'] = models.Batch.objects.all()
        context['purifications'] = models.Purification.objects.all()
        return context


class OrderCreateView(LoginRequiredMixin, CreateView):
    model = models.Order
    form_class = forms.OrderForm
    template_name = 'oligoshell/order_create.html'
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super(OrderCreateView, self).get_context_data(**kwargs)
        context['formset'] = forms.SequenceFormset(queryset=models.Sequence.objects.none())
        context['orders'] = models.Order.objects.all()
        context['batches'] = models.Batch.objects.all()
        context['purifications'] = models.Purification.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        form = forms.OrderForm(request.POST)
        formset = forms.SequenceFormset(request.POST)
        if form.is_valid() and formset.is_valid():
            new_form = form.save()
            formset = forms.SequenceFormset(request.POST, instance=new_form)
            formset.save()
            return redirect('/')
        return render(request, 'oligoshell/order_create.html', {'form': form, 'formset': formset})


class OrderUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Order
    template_name = 'oligoshell/order_detail.html'
    form_class = forms.OrderCommentsForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders'] = models.Order.objects.all()
        context['batches'] = models.Batch.objects.all()
        context['purifications'] = models.Purification.objects.all()
        return context

    def get_success_url(self):
        return reverse('oligoshell:order_detail', kwargs={'pk': self.object.id})


class BatchCreateView(LoginRequiredMixin, CreateView):
    template_name = 'oligoshell/batch_create.html'
    form_class = forms.BatchForm
    # success_url = reverse_lazy('oligoshell:batch_details')

    def get_success_url(self):
        return reverse('oligoshell:batch_details', kwargs={'pk': self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders'] = models.Order.objects.all()
        context['batches'] = models.Batch.objects.all()
        context['purifications'] = models.Purification.objects.all()
        return context


class BatchUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Batch
    template_name = 'oligoshell/batch_detail.html'
    form_class = forms.BatchCommentsForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders'] = models.Order.objects.all()
        context['batches'] = models.Batch.objects.all()
        context['purifications'] = models.Purification.objects.all()
        return context

    def get_success_url(self):
        return reverse('oligoshell:batch_details', kwargs={'pk': self.object.id})


class PurificationCreateView(LoginRequiredMixin, CreateView):
    model = models.Purification
    template_name = 'oligoshell/purification_create.html'
    form_class = forms.PurificationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders'] = models.Order.objects.all()
        context['batches'] = models.Batch.objects.all()
        context['purifications'] = models.Purification.objects.all()
        return context

    def get_success_url(self):
        return reverse('oligoshell:purification_details', kwargs={'pk': self.object.id})


class PurificationUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Purification
    template_name = 'oligoshell/purification_detail.html'
    form_class = forms.PurificationCommentsForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders'] = models.Order.objects.all()
        context['batches'] = models.Batch.objects.all()
        context['purifications'] = models.Purification.objects.all()
        return context

    def get_success_url(self):
        return reverse('oligoshell:purification_details', kwargs={'pk': self.object.id})


def register(request):
    if request.method == "POST":
        user_form = forms.UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(
                user_form.cleaned_data['password']
            )
            new_user.save()
            group = Group.objects.get(name='customer')
            new_user.groups.add(group)
            models.Profile.objects.create(user=new_user,
                                          photo='unknown.jpeg')
            return render(request, 'oligoshell/complete_registration.html',
                          {'new_user': new_user})
    else:
        user_form = forms.UserRegistrationForm()
    return render(request, 'oligoshell/register.html', {'form': user_form})


@login_required
def view_profile(request):
    return render(request, 'oligoshell/profile.html', {'user': request.user})


class SearchResultsListView(LoginRequiredMixin, ListView):
    model = models.Sequence
    context_object_name = 'sequences'
    template_name = 'oligoshell/search_results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders'] = models.Order.objects.all()
        context['batches'] = models.Batch.objects.all()
        context['purifications'] = models.Purification.objects.all()
        return context

    def get_queryset(self):
        query = self.request.GET.get('q')
        return models.Sequence.objects.filter(
            Q(seq_name__icontains=query) | Q(sequence__icontains=query)
        )
