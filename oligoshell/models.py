from django.db import models


class Sequence(models.Model):
    MIN_SCALE = '50 nmol'
    MED_SCALE = '200 nmol'
    MAX_SCALE = '1 umol'
    SCALES_CHOICES = [
        (MIN_SCALE, '50 nmol'),
        (MED_SCALE, '200 nmol'),
        (MAX_SCALE, '1 umol'),
    ]

    seq_name = models.CharField(verbose_name='Name', max_length=50)
    sequence = models.CharField(verbose_name="Sequence, 5'->3'", max_length=300)
    scale = models.CharField(
        max_length=20,
        choices=SCALES_CHOICES,
        default=MIN_SCALE,
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Sequences'
        verbose_name = 'Sequence'
        ordering = ['pk']

    # def __str__(self):
    #     return self.seq_name + " " + self.sequence
