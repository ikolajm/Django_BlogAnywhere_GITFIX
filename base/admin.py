from django.contrib import admin

# Register your models here.
from .models import User, Post, Comment, PostLike, CommentLike

admin.site.register(User)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(PostLike)
admin.site.register(CommentLike)