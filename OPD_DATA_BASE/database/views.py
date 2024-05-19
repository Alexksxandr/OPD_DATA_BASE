from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView, ListView, DeleteView, \
    UpdateView, DetailView, View
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import FileResponse, Http404
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied
from django.db.models import Q, F, Subquery, OuterRef, Count
from datetime import datetime
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


class AccountLogoutView(LoginRequiredMixin, LogoutView):
    pass


class LibraryView(ListView):
    template_name = 'main/elibrary.html'
    paginate_by = 30

    def get_queryset(self):
        query = self.request.GET.get('query')
        keywords = self.request.GET.get('keywords')
        keywords_block = self.request.GET.get('keywords_block')
        all_terms = self.request.GET.get('all_terms')
        queryset = Article.objects.filter(is_active=True,
                                          author__is_active=True).order_by(
            '-date_created')
        if query:
            search_terms = [term.strip() for term in query.split(',')]
            q_objects = Q()
            for term in search_terms:
                q_objects_temp = Q()
                date_term = None
                for fmt in (
                        "%d.%m.%Y", "%d.%m.%y", "%m.%d.%Y", "%m.%d.%y"):
                    try:
                        date_term = datetime.strptime(term, fmt).date()
                        q_objects_temp |= Q(date_created__date=date_term)
                        break
                    except ValueError:
                        pass
                if not date_term:
                    try:
                        day = int(term)
                        q_objects_temp |= Q(date_created__day=day)
                    except ValueError:
                        pass
                    try:
                        month = int(term)
                        q_objects_temp |= Q(date_created__month=month)
                    except ValueError:
                        pass
                    try:
                        year = int(term)
                        q_objects_temp |= Q(date_created__year=year)
                    except ValueError:
                        pass
                    q_objects_temp |= (
                            Q(title__iregex=term) |
                            Q(abstract__iregex=term) |
                            Q(author__fullname__iregex=term) |
                            Q(keywords__word__iregex=term)
                    )
                if all_terms:
                    q_objects &= q_objects_temp
                else:
                    q_objects |= q_objects_temp
            queryset = queryset.filter(q_objects).distinct()
        if keywords_block:
            keywords = [word.upper().strip() for word in keywords.split(',')]
            article_keywords = Article.objects.filter(
                pk=OuterRef('pk'),
                keywords__word__in=keywords).values(
                'pk').annotate(num_keywords=Count('keywords')).values(
                'num_keywords')
            queryset = queryset.annotate(
                num_keywords=Subquery(article_keywords)
            ).filter(num_keywords=len(keywords))
        return queryset


class DeleteArticleView(LoginRequiredMixin, DeleteView):
    model = Article
    success_url = reverse_lazy('library')
    template_name = 'main/delete_article.html'

    def form_valid(self, form):
        if self.object.author.id == self.request.user.id:
            return super().form_valid(form)
        raise PermissionDenied("У вас нет прав для удаления данной статьи.")


class CreateArticleView(LoginRequiredMixin, CreateView):
    model = Article
    fields = ['title', 'abstract', 'article', 'keywords_temp']
    template_name = 'main/create_article.html'
    success_url = reverse_lazy('library')

    def form_valid(self, form):
        if self.request.user.role == 2:
            form.instance.author = self.request.user
            response = super().form_valid(form)
            keywords = form.cleaned_data.get('keywords_temp', '').split(',')
            for word in keywords:
                word = word.upper().strip()
                if word:
                    keyword, created = Keyword.objects.get_or_create(word=word)
                    self.object.keywords.add(keyword)
            return response
        raise PermissionDenied("У вас нет прав для загрузки статьи.")


class UpdateArticleView(LoginRequiredMixin, UpdateView):
    model = Article
    fields = []
    template_name = 'main/update_article.html'
    success_url = reverse_lazy('library')

    def form_valid(self, form):
        if form.instance.author.id == self.request.user.id:
            form.instance.is_active = False
            return super().form_valid(form)
        raise PermissionDenied(
            "У вас нет прав для редактирования данной статьи.")


class ArticleView(LoginRequiredMixin, DetailView):
    model = Article
    template_name = 'main/article.html'

    def get_object(self, queryset=None):
        queryset = self.get_queryset()
        article = super().get_object(queryset=queryset)
        if not article.is_active or not article.author.is_active:
            raise Http404("Статья не найдена или ещё не проверена модерацией.")
        return article

    def get(self, request, *args, **kwargs):
        article = self.get_object()
        if request.user != article.author:
            article.views = F('views') + 1
            article.save()
        return super().get(request, *args, **kwargs)


class ProfileView(LoginRequiredMixin, DetailView):
    model = Account
    template_name = 'main/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        articles = context['object'].articles.all()
        articles = articles.filter(is_active=True) | articles.filter(
            author=user)
        context['articles'] = articles
        return context

    def get(self, request, *args, **kwargs):
        author = self.get_object()
        if not author.is_active:
            return redirect('library')
        return super().get(request, *args, **kwargs)


class UpdateAccountView(LoginRequiredMixin, UpdateView):
    model = Account
    fields = ['first_name', 'last_name', 'third_name']
    template_name = 'main/update_account.html'

    def get_success_url(self):
        return reverse_lazy('profile', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        if form.instance.id == self.request.user.id:
            return super().form_valid(form)
        raise PermissionDenied(
            "У вас нет прав для редактирования этого профиля.")


class DownloadView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        article = get_object_or_404(Article, slug=kwargs['slug'])
        file = article.article
        if request.user != article.author:
            article.downloads = F('downloads') + 1
            article.save()
        response = FileResponse(file.open(), as_attachment=True,
                                filename=file.name)
        return response
