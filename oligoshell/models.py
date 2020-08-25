from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings

from . import validators
from . import utils


class Order(models.Model):
    customer = models.CharField(verbose_name='Customer Name',
                                max_length=50)
    comments = models.TextField(max_length=300,
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

    def __str__(self):
        return '# ' + str(self.pk) + ' by ' + str(self.customer)


class Sequence(models.Model):
    MIN_SCALE = '50 nmol'
    MED_SCALE = '200 nmol'
    MAX_SCALE = '1 umol'
    SCALES_CHOICES = [
        (MIN_SCALE, '50 nmol'),
        (MED_SCALE, '200 nmol'),
        (MAX_SCALE, '1 umol'),
    ]

    APPEARANCE_20mM = '20 mM'
    APPEARANCE_100mM = '100 mM'
    APPEARANCE_Freeze_dried = 'Freeze-dried'
    APPEARANCE_CHOICES = [
        (APPEARANCE_20mM, '20 mM'),
        (APPEARANCE_100mM, '100 mM'),
        (APPEARANCE_Freeze_dried, 'Freeze-dried'),
    ]

    PURIFICATION_OPC = 'OPC'
    PURIFICATION_RP_HPLC = 'RP-HPLC'
    PURIFICATION_IEX_HPLC = 'IEX-HPLC'
    PURIFICATION_PAGE = 'PAGE'
    PURIFICATION_PAGE_HPLC = 'PAGE + HPLC'
    PURIFICATION_RECOMMENDED = 'Company Recommended'
    PURIFICATION_CHOICES = [
        (PURIFICATION_OPC, 'OPC'),
        (PURIFICATION_RP_HPLC, 'RP-HPLC'),
        (PURIFICATION_IEX_HPLC, 'IEX-HPLC'),
        (PURIFICATION_PAGE, 'PAGE'),
        (PURIFICATION_PAGE_HPLC, 'PAGE + HPLC'),
        (PURIFICATION_RECOMMENDED, 'Company Recommended'),
    ]

    seq_name = models.CharField(verbose_name='Name',
                                max_length=50,
                                validators=[validators.validate_seq_name_regex])

    sequence = models.CharField(verbose_name="Sequence, 5'->3'",
                                max_length=300,
                                validators=[validators.validate_sequence_regex,
                                            validators.validate_modifications])

    scale = models.CharField(verbose_name='Synthesis Scale',
                             max_length=20,
                             choices=SCALES_CHOICES,
                             default=MIN_SCALE
                             )

    appearance_requested = models.CharField(verbose_name='Appearance',
                                            max_length=20,
                                            choices=APPEARANCE_CHOICES,
                                            default=APPEARANCE_20mM
                                            )

    purification_requested = models.CharField(verbose_name='Purification',
                                              max_length=30,
                                              choices=PURIFICATION_CHOICES,
                                              default=PURIFICATION_OPC
                                              )

    epsilon260 = models.IntegerField(verbose_name='Extinction Coefficient', blank=True, null=True)

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='sequences')

    created = models.DateTimeField(verbose_name='Sequence Created', auto_now_add=True)
    updated = models.DateTimeField(verbose_name='Sequence Updated', auto_now=True)

    def save(self, *args, **kwargs):
        """Save extinction coefficient to the model"""
        unmodified_list, unmodified_degenerated_list, modification_list = utils.sequence2lists(self.sequence)
        self.epsilon260 = (sum((utils.extinction_dna_nn(item) for item in unmodified_list)) +
                           sum((utils.extinction_dna_simple(item) for item in unmodified_degenerated_list)) +
                           sum((utils.modification_extinction_260[item] for item in modification_list)))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.seq_name + ', ' + self.sequence

    class Meta:
        verbose_name_plural = 'Sequences'
        verbose_name = 'Sequence'
        ordering = ['pk']


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    birthday = models.DateTimeField(blank=True, null=True)
    photo = models.ImageField(upload_to="user/%Y/%m/%d/", blank=True)


class Batch(models.Model):
    title = models.CharField(verbose_name='Batch Name', max_length=200)
    created = models.DateTimeField(verbose_name='Batch Created', auto_now_add=True)
    sequences2synthesis = models.ManyToManyField(Sequence,
                                                 verbose_name='Sequences to be Synthesized',
                                                 related_name='batches')
    notes = models.TextField(verbose_name='Notes', blank=True, null=True)

    def get_absolute_url(self):
        return reverse('oligoshell:batch_details', args=[self.pk])

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Batches'
        verbose_name = 'Batch'
        ordering = ['pk']


class Purification(models.Model):
    OPC = 'OPC'
    RP_HPLC = 'RP-HPLC'
    IEX_HPLC = 'IEX-HPLC'
    PAGE = 'PAGE'
    PURIFICATION_CHOICES = [
        (OPC, 'OPC'),
        (RP_HPLC, 'RP-HPLC'),
        (IEX_HPLC, 'IEX-HPLC'),
        (PAGE, 'PAGE'),
    ]

    title = models.CharField(verbose_name='Purification Method',
                             max_length=50,
                             choices=PURIFICATION_CHOICES,
                             default=OPC,
                             )

    created = models.DateTimeField(verbose_name='Purification Created',
                                   auto_now_add=True)

    pur_seqs = models.ManyToManyField(Sequence,
                                      verbose_name='Sequences for Purification',
                                      related_name='purifications')


    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Purifications'
        verbose_name = 'Purification'
        ordering = ['pk']
