from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='main'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.AccountLoginView.as_view(), name='login'),
    path('logout/', views.AccountLogoutView.as_view(), name='logout'),
    path('library/', views.LibraryView.as_view(), name='library'),
    path('library/create/', views.CreateArticleView.as_view(),
         name='create_article'),
    path('library/<pk>/delete/', views.DeleteArticleView.as_view(),
         name='delete_article'),
    path('library/<pk>/update/', views.UpdateArticleView.as_view(),
         name='update_article'),
    path('library/<pk>/', views.ArticleView.as_view(), name='article')
    ]

