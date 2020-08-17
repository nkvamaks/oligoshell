from django.db import models
from django.core import validators


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
                                validators=[validators.RegexValidator(
                                    regex='^[-a-zA-Z0-9_()]+$',
                                    message="Name should contain letters, numbers and special characters  _ ( )"
                                )])

    sequence = models.CharField(verbose_name="Sequence, 5'->3'",
                                max_length=300,
                                validators=[validators.RegexValidator(
                                    regex='^(((\[[-\._a-zA-Z0-9]+\])*?[aAcCgGtTwWsSmMkKrRyYbBdDhHvVnN]*?)*?)$',
                                    message="Sequence should contain A/C/G/T, degenerated bases W/S/M/K/R/Y/B/D/H/V/N, and modifications e.g. [FAM], [BHQ1] etc."
                                )])

    scale = models.CharField(max_length=20,
                             choices=SCALES_CHOICES,
                             default=MIN_SCALE
                             )

    appearance_requested = models.CharField(max_length=20,
                                            choices=APPEARANCE_CHOICES,
                                            default=APPEARANCE_20mM
                                            )

    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='sequences')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Sequences'
        verbose_name = 'Sequence'
        ordering = ['pk']

