from django.db import models
from django.urls import reverse
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import m2m_changed
# from datetime import datetime
# from django.utils.timezone import now
# from django.contrib.auth.models import User


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
        ordering = ['pk']

    def get_absolute_url(self):
        return reverse('oligoshell:index')

    def __str__(self):
        return '# ' + str(self.pk) + ' by ' + str(self.customer)


class Sequence(models.Model):
    MIN_SCALE = '50 nmole'
    MED_SCALE = '200 nmole'
    MAX_SCALE = '1 umole'
    X_SCALE = '2 umole'
    XX_SCALE = '5 umole'
    XXX_SCALE = '10 umole'
    SCALES_CHOICES = [
        (MIN_SCALE, '50 nmole DNA oligo'),
        (MED_SCALE, '200 nmole DNA oligo'),
        (MAX_SCALE, '1 \xb5mole DNA oligo'),
        (X_SCALE, '2 \xb5mole DNA oligo'),
        (XX_SCALE, '5 \xb5mole DNA oligo'),
        (XXX_SCALE, '10 \xb5mole DNA oligo'),
    ]

    FORMAT_100uM = '100 uM'
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
                                validators=[validators.validate_syntax])

    scale = models.CharField(verbose_name='Scale',
                             max_length=20,
                             choices=SCALES_CHOICES,
                             default=MIN_SCALE
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

    volume = models.FloatField(verbose_name='Total Volume, mL', blank=True, null=True)

    concentration = models.FloatField(verbose_name='Concentration, uM', blank=True, null=True)

    length = models.IntegerField(verbose_name='Sequence Length', blank=True, null=True)

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='sequences')

    created = models.DateTimeField(verbose_name='Sequence Created', auto_now_add=True)
    updated = models.DateTimeField(verbose_name='Sequence Updated', auto_now=True)

    synthesized = models.BooleanField(verbose_name='Sequence Synthesized', default=False)
    done = models.BooleanField(verbose_name='Sequence Complete', default=False)

    def set_synthesized(self):
        self.synthesized = True
        self.save()

    def save(self, *args, **kwargs):
        self.sequence = self.sequence.upper()
        if not self.epsilon260:
            unmodified_list, unmodified_degenerated_list, modification_list = utils.sequence2lists(self.sequence)
            self.epsilon260 = (sum((utils.extinction_dna_nn(item) for item in unmodified_list)) +
                               sum((utils.extinction_dna_simple(item) for item in unmodified_degenerated_list)) +
                               sum((utils.modification_extinction_260[item] for item in modification_list)))
            # self.length = (
            #         len(''.join(unmodified_list)) +
            #         len(''.join(unmodified_degenerated_list)) +
            #         len(modification_list)
            # )
        #print(utils.sequence2tuple(self.sequence))
        if self.absorbance260:
            self.concentration = round(self.absorbance260 / self.epsilon260 * 1000000, 2)
        if self.sequence and not self.absorbance260:
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
    title = models.CharField(verbose_name='Batch ID', max_length=100)
    created = models.DateTimeField(verbose_name='Batch Created', auto_now_add=True)
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
    RP_HPLC = 'RP-HPLC'
    IEX_HPLC = 'IEX-HPLC'
    PAGE = 'PAGE'
    PURIFICATION_CHOICES = [
        (DESALT, 'Desalt'),
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

    class Meta:
        verbose_name_plural = 'Purifications'
        verbose_name = 'Purification'
        ordering = ['-pk']
