from django.urls import path
from . import views

urlpatterns = [
    path('', views.feed, name='feed'),
    path('post/<str:pk>/', views.post, name='post'),
    path('activity/', views.activityFeed, name='activity'),
    path('create-post/', views.createPost, name='create-post'),
    path('edit-post/<str:pk>/', views.updatePost, name='edit-post'),
    path('delete-post/<str:pk>/', views.deletePost, name='delete-post'),
    path('edit-comment/<str:pk>/', views.updateComment, name='edit-comment'),
    path('delete-comment/<str:pk>/', views.deleteComment, name='delete-comment'),
    
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name="logout"),
    path('register/', views.registerUser, name="register"),

    path('profile/<str:pk>/', views.userProfile, name='profile'),
    path('update-user/', views.updateUser, name='update-user'),
]