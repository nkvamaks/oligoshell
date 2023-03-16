from django.db import models
from django.urls import reverse
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import m2m_changed

from . import validators
from . import utils


class Order(models.Model):
    customer = models.CharField(verbose_name='Customer Name',
                                max_length=50,
                                )
    comments = models.CharField(max_length=300,
                                blank=True,
                                null=True,
                                )
    email = models.EmailField(blank=True, null=True)
    created = models.DateTimeField(verbose_name='Date Ordered',
                                   auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Orders'
        verbose_name = 'Order number'
        ordering = ['-pk']

    def get_absolute_url(self):
        return reverse('oligoshell:index')

    def __str__(self):
        return '# ' + str(self.pk) + ' by ' + str(self.customer)


class Sequence(models.Model):
    MIN_SCALE = '50'
    MED_SCALE = '200'
    MAX_SCALE = '1000'
    X_SCALE = '2000'
    XX_SCALE = '5000'
    XXX_SCALE = '10000'
    SCALES_CHOICES = [
        (MIN_SCALE, '50 nmole oligo'),
        (MED_SCALE, '200 nmole oligo'),
        (MAX_SCALE, '1 \xb5mole oligo'),
        (X_SCALE, '2 \xb5mole oligo'),
        (XX_SCALE, '5 \xb5mole oligo'),
        (XXX_SCALE, '10 \xb5mole oligo'),
    ]

    FORMAT_100uM = '100 \xb5M'
    FORMAT_Freeze_dry = 'Freeze-dry'
    FORMAT_CHOICES = [
        (FORMAT_100uM, '100 \xb5M in milli-Q'),
        (FORMAT_Freeze_dry, 'Freeze-dry'),
    ]

    PURIFICATION_DESALT = 'Desalt'
    PURIFICATION_CARTRIDGE = 'Cartridge'
    PURIFICATION_HPLC = 'HPLC'
    PURIFICATION_PAGE = 'PAGE'
    PURIFICATION_RECOMMENDED = 'Company Recommended'
    PURIFICATION_CHOICES = [
        (PURIFICATION_DESALT, 'Desalt'),
        (PURIFICATION_CARTRIDGE, 'Cartridge'),
        (PURIFICATION_HPLC, 'HPLC'),
        (PURIFICATION_PAGE, 'PAGE'),
        (PURIFICATION_RECOMMENDED, 'Company Recommended'),
    ]

    seq_name = models.CharField(verbose_name='Sequence Name',
                                max_length=50,
                                validators=[validators.validate_seq_name_regex])

    sequence = models.CharField(verbose_name="Sequence, 5'->3'",
                                max_length=300,
                                validators=[validators.validate_seq])

    scale = models.CharField(verbose_name='Scale',
                             max_length=20,
                             choices=SCALES_CHOICES,
                             default=MED_SCALE
                             )

    format_requested = models.CharField(verbose_name='Format',
                                        max_length=20,
                                        choices=FORMAT_CHOICES,
                                        default=FORMAT_100uM
                                        )

    purification_requested = models.CharField(verbose_name='Purification',
                                              max_length=30,
                                              choices=PURIFICATION_CHOICES,
                                              default=PURIFICATION_DESALT
                                              )

    epsilon260 = models.IntegerField(verbose_name='Extinction Coefficient', blank=True, null=True)
    absorbance260 = models.FloatField(verbose_name='Absorbance at 260 nm', blank=True, null=True)
    volume = models.FloatField(verbose_name='Volume, mL', blank=True, null=True)
    concentration = models.FloatField(verbose_name='Concentration, uM', blank=True, null=True)
    dilution_factor = models.FloatField(verbose_name='Dilution Factor', blank=True, null=True)
    length = models.IntegerField(verbose_name='Sequence Length', blank=True, null=True)
    mass_monoisotopic = models.FloatField(verbose_name='Monoisotopic Mass', blank=True, null=True)
    mass_average = models.FloatField(verbose_name='Average Mass', blank=True, null=True)

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='sequences')

    created = models.DateTimeField(verbose_name='Sequence Created', auto_now_add=True)
    updated = models.DateTimeField(verbose_name='Sequence Updated', auto_now=True)

    synthesized = models.BooleanField(verbose_name='Sequence Synthesized', default=False)
    done = models.BooleanField(verbose_name='Sequence Complete', default=False)

    def set_synthesized(self):
        self.synthesized = True
        self.save()

    def get_odu260(self):
        if self.absorbance260 and self.dilution_factor and self.volume:
            return round(self.absorbance260 * self.dilution_factor * self.volume, 2)
        else:
            return 0

    def get_quantity(self):
        if self.concentration and self.volume:
            return round(self.concentration * self.volume, 1)
        else:
            return 0

    def get_mass_average_dmt_on(self):
        if self.mass_average:
            return round(self.mass_average + utils.mass_avg['DMT'] - utils.mass_avg['H'], 2)
        else:
            return 0

    def get_mass_monoisotopic_dmt_on(self):
        if self.mass_monoisotopic:
            return round(self.mass_monoisotopic + utils.mass_mono['DMT'] - utils.mass_mono['H'], 4)
        else:
            return None

    def generate_esi_series(self):
        for z in range(1, self.length):
            esi_series_avg_dmt_off = round((self.mass_average - z * utils.mass_avg['H']) / z, 2)
            esi_series_avg_dmt_on = round((self.get_mass_average_dmt_on() - z * utils.mass_avg['H']) / z, 2)
            if not utils.contain_degenerate_nucleotide(self.sequence):
                esi_series_mono_dmt_off = round((self.mass_monoisotopic - z * utils.mass_mono['H']) / z, 4)
                esi_series_mono_dmt_on = round((self.get_mass_monoisotopic_dmt_on() - z * utils.mass_mono['H']) / z, 4)
            else:
                esi_series_mono_dmt_off = None
                esi_series_mono_dmt_on = None
            yield z, esi_series_avg_dmt_off, esi_series_avg_dmt_on, esi_series_mono_dmt_off, esi_series_mono_dmt_on

    def save(self, *args, **kwargs):
        if not self.epsilon260:
            self.epsilon260 = utils.get_extinction(self.sequence)
        if not self.length:
            self.length = utils.get_length(self.sequence)
        if not self.mass_average:
            self.mass_average = utils.get_mass_avg(self.sequence)
        if not self.mass_monoisotopic and not utils.contain_degenerate_nucleotide(self.sequence):
            self.mass_monoisotopic = utils.get_mass_monoisotopic(self.sequence)
        if self.absorbance260 and self.dilution_factor:
            self.concentration = round(self.absorbance260 * self.dilution_factor / self.epsilon260 * 1000000, 2)
        if self.sequence and not (self.absorbance260 and self.dilution_factor):
            self.concentration = 0
        if self.concentration:
            self.done = True
        else:
            self.done = False
        super().save(*args, **kwargs)

    def __str__(self):
        return self.seq_name + ' (' + self.order.customer + ')' + ', ' + self.sequence + ', ' + self.scale

    class Meta:
        verbose_name_plural = 'Sequences'
        verbose_name = 'Sequence'
        ordering = ['pk']


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    birthday = models.DateTimeField(blank=True, null=True)
    photo = models.ImageField(upload_to="user/%Y/%m/%d/", blank=True)


class Batch(models.Model):
    title = models.CharField(verbose_name='OligoSynthesis ID', max_length=100)
    created = models.DateTimeField(verbose_name='Created', auto_now_add=True)
    sequences2synthesis = models.ManyToManyField(Sequence,
                                                 verbose_name='Sequences for Synthesis',
                                                 related_name='batches')
    comments = models.CharField(max_length=300, verbose_name='Comments', blank=True, null=True)

    def get_absolute_url(self):
        return reverse('oligoshell:batch_details', args=[self.pk])

    class Meta:
        verbose_name_plural = 'Batches'
        verbose_name = 'Batch'
        ordering = ['-pk']


@receiver(m2m_changed, sender=Batch.sequences2synthesis.through)
def sequence_synthesized(sender, **kwargs):
    action = kwargs.pop('action', None)
    pk_set = kwargs.pop('pk_set', None)
    instance = kwargs.pop('instance', None)
    if action == 'post_add':
        for id_num in pk_set:
            instance.sequences2synthesis.get(pk=id_num).set_synthesized()


class Purification(models.Model):
    DESALT = 'Desalt'
    CARTRIDGE = 'Cartridge'
    RP_HPLC = 'RP-HPLC'
    IEX_HPLC = 'IEX-HPLC'
    PAGE = 'PAGE'
    PURIFICATION_CHOICES = [
        (DESALT, 'Desalt'),
        (CARTRIDGE, 'Cartridge'),
        (RP_HPLC, 'RP-HPLC'),
        (IEX_HPLC, 'IEX-HPLC'),
        (PAGE, 'PAGE'),
    ]

    title = models.CharField(verbose_name='Purification ID', max_length=100)

    pur_method = models.CharField(verbose_name='Purification Method',
                                  max_length=50,
                                  choices=PURIFICATION_CHOICES,
                                  default=DESALT,
                                  )

    created = models.DateTimeField(verbose_name='Purification Created',
                                   auto_now_add=True)

    pur_seqs = models.ManyToManyField(Sequence,
                                      verbose_name='Sequences Available for Purification',
                                      related_name='purifications',
                                      )

    comments = models.CharField(max_length=300, verbose_name='Comments', blank=True, null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('oligoshell:purification_details', args=[self.pk])

    class Meta:
        verbose_name_plural = 'Purifications'
        verbose_name = 'Purification'
        ordering = ['-pk']
