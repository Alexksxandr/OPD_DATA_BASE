from django.shortcuts import render
from django.views.generic import CreateView, ListView, DeleteView, \
    UpdateView, DetailView
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseRedirect
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


class LibraryView(ListView):
    template_name = 'main/elibrary.html'

    def get_queryset(self):
        return Article.objects.filter(is_active=True)


class DeleteArticleView(DeleteView):
    model = Article
    success_url = reverse_lazy('library')
    template_name = 'main/delete_article.html'

    def form_valid(self, form):
        if self.object.author.id == self.request.user.id:
            return super().form_valid(form)
        return HttpResponseRedirect(self.get_success_url())


class CreateArticleView(CreateView):
    model = Article
    fields = ['title', 'abstract', 'article', 'keywords']
    template_name = 'main/create_article.html'
    success_url = reverse_lazy('library')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class UpdateArticleView(UpdateView):
    model = Article
    fields = []
    template_name = 'main/update_article.html'
    success_url = reverse_lazy('library')

    def form_valid(self, form):
        if form.instance.author.id == self.request.user.id:
            return super().form_valid(form)
        return HttpResponseRedirect(self.get_success_url())


class ArticleView(DetailView):
    model = Article
    template_name = 'main/article.html'
