from django.contrib import admin

from . import models


@admin.register(models.Sequence)
class SequenceAdmin(admin.ModelAdmin):

    list_display = ('seq_name', 'sequence', 'scale')
    list_display_links = ('seq_name', 'sequence')
    search_fields = ('seq_name', 'sequence')
    list_filter = ('scale', 'created')
    ordering = ('created',)
