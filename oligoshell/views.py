from django.views.generic import ListView
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.views.generic.edit import CreateView
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.exceptions import ValidationError

from . import models
from . import forms
from . import utils


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

    def get_form_kwargs(self):
        """ Passes the request object to the form class. """
        kwargs = super(OrderCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def post(self, request, *args, **kwargs):
        form = forms.OrderForm(request.POST, request.FILES, request=request)
        formset = forms.SequenceFormset(request.POST)

        if request.FILES and form.is_valid():
            new_form = form.save(commit=False)
            data = request.FILES['bulk_seqs'].read().decode('utf-8-sig')
            seqdict_from_file = utils.get_seqdict_from_file(data)
            post = request.POST.copy()  # to make it mutable
            print(post)
            post = post | seqdict_from_file
            # post.update(seqdict_from_file)
            print(post)
            request.POST = post  # update request.POST with the data from file
            formset = forms.SequenceFormset(request.POST, instance=new_form)
            return render(request, 'oligoshell/order_create.html', {'form': form, 'formset': formset})

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
            Q(seq_name__icontains=query) | Q(sequence__icontains=query) | Q(pk__icontains=query)
        )


def calc_view(request):
    form = forms.CalcForm(request.POST or None)
    sequence = ''
    length = 0
    epsilon260 = 0
    absorbance260 = 0
    dilution_factor = 0
    concentration_molar = 0
    concentration_mass = 0
    volume = 0
    odu260 = 0
    quantity = 0
    mass_monoisotopic = 0
    mass_monoisotopic_dmt_on = 0
    mass_average = 0
    mass_average_dmt_on = 0
    esi_series = []
    seq_wo_phosph_tup = ()
    mass_fragments_array = []

    if form.is_valid():
        sequence = form.cleaned_data['sequence']
        volume = form.cleaned_data['volume']
        absorbance260 = form.cleaned_data['absorbance260']
        dilution_factor = form.cleaned_data['dilution_factor']
        length = utils.get_length(sequence)
        epsilon260 = utils.get_extinction(sequence)
        if not utils.contain_degenerate_nucleotide(sequence):
            mass_monoisotopic = utils.get_mass_monoisotopic(sequence)
            mass_monoisotopic_dmt_on = round(mass_monoisotopic + utils.mass_mono['DMT'] - utils.mass_mono['H'], 4)
        mass_average = utils.get_mass_avg(sequence)
        mass_average_dmt_on = round(mass_average + utils.mass_avg['DMT'] - utils.mass_avg['H'], 2)

        for z in range(1, length):
            esi_series_avg_dmt_off = round((mass_average - z * utils.mass_avg['H']) / z, 2)
            esi_series_avg_dmt_on = round((mass_average_dmt_on - z * utils.mass_avg['H']) / z, 2)
            if not utils.contain_degenerate_nucleotide(sequence):
                esi_series_mono_dmt_off = round((mass_monoisotopic - z * utils.mass_mono['H']) / z, 4)
                esi_series_mono_dmt_on = round((mass_monoisotopic_dmt_on - z * utils.mass_mono['H']) / z, 4)
            else:
                esi_series_mono_dmt_off = None
                esi_series_mono_dmt_on = None
            esi_series.append((z, esi_series_avg_dmt_off, esi_series_avg_dmt_on, esi_series_mono_dmt_off, esi_series_mono_dmt_on))

        if absorbance260 and dilution_factor:
            concentration_molar = round(absorbance260 * dilution_factor / epsilon260 * 1000000, 2)
            concentration_mass = round(concentration_molar * mass_average / 1000, 2)

        if absorbance260 and dilution_factor and volume:
            odu260 = round(absorbance260 * dilution_factor * volume, 2)

        if concentration_molar and volume:
            quantity = round(concentration_molar * volume, 1)

        if not utils.contain_degenerate_nucleotide(sequence):
            seq_wo_phosph_tup = utils.sequence_split(utils.sequence_explicit(sequence))[::2]
            a_esi, a_B_esi, b_esi, c_esi, d_esi, w_esi, x_esi, y_esi, z_esi = map(utils.get_ms_fragments_esi_series, utils.get_ms_fragments(sequence))

            for charge in range(1, length):
                mass_fragments_array.append(
                    [
                        (d_esi[seq_ind][charge-1],
                         c_esi[seq_ind][charge-1],
                         b_esi[seq_ind][charge-1],
                         a_esi[seq_ind][charge-1],
                         a_B_esi[seq_ind][charge-1],
                         seq_wo_phosph_tup[seq_ind-1],
                         w_esi[seq_ind][charge-1],
                         x_esi[seq_ind][charge-1],
                         y_esi[seq_ind][charge-1],
                         z_esi[seq_ind][charge-1]) for seq_ind in range(1, length+1)
                    ]
                )

    return render(request, 'oligoshell/calculator.html', {
        'form': form,
        'sequence': sequence,
        'length': length,
        'charge': range(1, length),
        'epsilon260': epsilon260,
        'absorbance260': absorbance260,
        'dilution_factor': dilution_factor,
        'concentration_molar': concentration_molar,
        'concentration_mass': concentration_mass,
        'volume': volume,
        'odu260': odu260,
        'quantity': quantity,
        'mass_monoisotopic': mass_monoisotopic,
        'mass_average': mass_average,
        'mass_monoisotopic_dmt_on': mass_monoisotopic_dmt_on,
        'mass_average_dmt_on': mass_average_dmt_on,
        'esi_series': esi_series,
        'seq_wo_phosph_tup': seq_wo_phosph_tup,
        'mass_fragments_array': mass_fragments_array,
        'orders': models.Order.objects.all(),
        'batches': models.Batch.objects.all(),
        'purifications': models.Purification.objects.all(),
    })
