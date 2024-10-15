from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Election


# Create your views here.

@login_required
def dashboard(request):

    user_elections = Election.objects.filter(user=request.user)
    return render(request, 'dashboard.html', {'elections': user_elections})
