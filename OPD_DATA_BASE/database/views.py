from django.shortcuts import render
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from .models import *
# Create your views here.


def index(request):
    return render(request, 'main/index.html')


class RegisterView(CreateView):
    model = Account
    fields = ['email', 'username', 'first_name', 'last_name', 'third_name',
              'password']
    template_name = 'main/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        form.instance.set_password(
            form.cleaned_data['password'])
        return super().form_valid(form)


class AccountLoginView(LoginView):
    template_name = 'main/login.html'


class AccountLogoutView(LogoutView):
    pass
