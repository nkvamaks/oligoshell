from django.shortcuts import render

from .models import Sequence


def index(request):
    sequences = Sequence.objects.all()
    context = {'sequences': sequences}
    return render(request, 'oligoshell/index.html', context)
