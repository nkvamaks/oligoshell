from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import Sequence

@login_required
def index(request):
    sequences = Sequence.objects.all()
    context = {'sequences': sequences}
    return render(request, 'oligoshell/index.html', context)
