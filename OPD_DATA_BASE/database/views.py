from django.shortcuts import render
from django.views.generic import CreateView, ListView, DeleteView, UpdateView, \
    DetailView, RedirectView
from django.urls import reverse_lazy
from .models import *
# Create your views here.
def index(request):
    return render(request, 'main/index.html')

