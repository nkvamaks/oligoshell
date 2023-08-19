from django.contrib import admin

from . import models


@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'birthday', 'photo')


@admin.register(models.Sequence)
class SequenceAdmin(admin.ModelAdmin):
    list_display = ('pk', 'seq_name', 'sequence', 'scale', 'format_requested', 'epsilon260',
                    'absorbance260', 'volume', 'concentration', 'synthesized')
    list_display_links = ('seq_name',)
    search_fields = ('seq_name', 'sequence')
    list_filter = ('scale', 'created')
    ordering = ('created',)


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'created', 'email', 'comments', 'bulk_seqs')
    search_fields = ('customer', 'email')
    list_filter = ('created',)
    ordering = ('created',)


@admin.register(models.Batch)
class BatchAdmin(admin.ModelAdmin): pass


@admin.register(models.Purification)
class PurificationAdmin(admin.ModelAdmin): pass
