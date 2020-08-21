from django.db import models
from django.contrib.auth.models import User

from django.conf import settings

from . import validators
from . import utils


class Order(models.Model):
    customer = models.CharField(verbose_name='Customer Name',
                                max_length=50)
    comments = models.TextField(blank=True, null=True)
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

    seq_name = models.CharField(verbose_name='Name',
                                max_length=50,
                                validators=[validators.validate_seq_name_regex])

    sequence = models.CharField(verbose_name="Sequence, 5'->3'",
                                max_length=300,
                                validators=[validators.validate_sequence_regex,
                                            validators.validate_modifications])

    scale = models.CharField(max_length=20,
                             choices=SCALES_CHOICES,
                             default=MIN_SCALE
                             )

    appearance_requested = models.CharField(max_length=20,
                                            choices=APPEARANCE_CHOICES,
                                            default=APPEARANCE_20mM
                                            )

    epsilon260 = models.IntegerField(verbose_name='Extinction Coefficient')

    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='sequences')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """Save extinction coefficient to the model"""
        unmodified_list, unmodified_degenerated_list, modification_list = utils.sequence2lists(self.sequence)
        self.epsilon260 = (sum((utils.extinction_dna_nn(item) for item in unmodified_list)) +
                           sum((utils.extinction_dna_simple(item) for item in unmodified_degenerated_list)) +
                           sum((utils.modification_extinction_260[item] for item in modification_list)))
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Sequences'
        verbose_name = 'Sequence'
        ordering = ['pk']


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    birthday = models.DateTimeField(blank=True, null=True)
    photo = models.ImageField(upload_to="user/%Y/%m/%d/", blank=True)
