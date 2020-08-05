from django.db import models


class Sequence(models.Model):
    seq_name = models.CharField(verbose_name='Name', max_length=25)
    sequence = models.CharField(verbose_name="Sequence, 5'->3'", max_length=300)

    class Meta:
        verbose_name_plural = 'Sequences'
        verbose_name = 'Sequence'
        ordering = ['pk']

    def __str__(self):
        return self.seq_name + " " + self.sequence
