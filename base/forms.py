from django.db.models.base import Model
from django.forms import ModelForm
from .models import User, Post, Comment
from django.contrib.auth.forms import UserCreationForm

class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'password1', 'password2']

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'bio']

class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = '__all__'
        exclude = ['author', 'participants', 'edited']

class PostEditForm(ModelForm):
    class Meta:
        model = Post
        fields = '__all__'
        exclude = ['author', 'participants', 'edited']

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = '__all__'
        exclude = ['author', 'edited', 'post']