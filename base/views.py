from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Post, Comment, PostLike, CommentLike, User
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import MyUserCreationForm, UserForm, PostForm, CommentForm

# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the index.")

def loginPage(request):
    page='login'
    if request.user.is_authenticated:
        return redirect('feed')

    if request.method == "POST":
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except:
            return messages.error(request, 'User does not exist')
        
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('feed')
        else:
            messages.error(request, 'Username or password does not exist')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)

# Logout user
def logoutUser(request):
    logout(request)
    return redirect('feed')

# Signup user
def registerUser(request):
    form = MyUserCreationForm()

    if request.method == "POST":
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('feed')
        else:
            messages.error(request, 'An error occurred during registrations')

    return render(request, 'base/login_register.html', { 'form': form })

# Main post feed view
def feed(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    filtered_posts = Post.objects.filter(
        Q(content__icontains = q)
    )
    post_count = filtered_posts.count()
    for post in filtered_posts:
        # Get post likes for checks
        likes = PostLike.objects.filter(post=post)
        post.likes = likes
        post.liked = False
        for like in post.likes:
            if request.user.id == like.user.id:
                post.liked = True
        # Get post comments for checks
        comments = Comment.objects.filter(post=post)
        post.comments = comments
        post.commented = False
        for comment in post.comments:
            if request.user.id ==  comment.author.id:
                post.commented = True



    # Concat all recent queries
    recent_activity = []

    # Set all recent post data - done
    # Get dicts
    recent_posts = Post.objects.all()[:3]
    # Get assc models with posts
    for post in recent_posts:
        # Get likes for post
        likes = PostLike.objects.filter(post=post)
        post.likes = likes
        post.type = "post"
        post.shorten = len(post.content) > 20
        strippedContent = post.content[0:20].strip()
        post.shortened = strippedContent + '...'
        post.liked = False
        for like in post.likes:
            if request.user.id == like.user.id:
                post.liked = True
        # Get post comments for checks
        comments = Comment.objects.filter(post=post)
        post.comments = comments
        post.commented = False
        for comment in post.comments:
            if request.user.id ==  comment.author.id:
                post.commented = True
        
        recent_activity.append(post)
    
    # Get all recent likes of posts - 
    recent_post_likes = PostLike.objects.all()[:3]
    for plike in recent_post_likes:
        # Get all likes of liked post
        likes = PostLike.objects.filter(post = plike.post)
        plike.post.likes = likes
        plike.type = "post_like"
        plike.post.shorten = len(plike.post.content) > 20
        strippedContent = plike.post.content[0:20].strip()
        plike.post.shortened = strippedContent + '...'

        # Append like and comment data to dict
        plike.post.liked = False
        for like in plike.post.likes:
            if request.user.id == like.user.id:
                plike.post.liked = True
        # Get post comments for checks
        comments = Comment.objects.filter(post=plike.post)
        plike.post.comments = comments
        plike.post.commented = False
        for comment in plike.post.comments:
            if request.user.id ==  comment.author.id:
                plike.post.commented = True
        
        recent_activity.append(plike)
    
    # Get all recent comments
    recent_comments = Comment.objects.all()[:3]
    for comment in recent_comments:
        # Get all likes of liked comment
        likes = CommentLike.objects.filter(comment = comment)
        comment.likes = likes
        comment.type = 'comment'
        comment.shorten = len(comment.content) > 25
        strippedContent = comment.content[0:25].strip()
        comment.shortened = strippedContent + '...'

        comment.liked = False
        for like in comment.likes:
            if request.user.id == like.user.id:
                comment.liked = True

        recent_activity.append(comment)
    
    # Get all recent likes of comments
    recent_comment_likes = CommentLike.objects.all()[:3]
    for clike in recent_comment_likes:
        # Get all likes of a liked comment
        likes = CommentLike.objects.filter(comment = clike.comment)
        clike.comment.likes = likes
        clike.type = 'comment_like'
        clike.comment.shorten = len(clike.comment.content) > 20
        strippedContent = clike.comment.content[0:20].strip()
        clike.comment.shortened = strippedContent + '...'

        # Append like and comment data to dict
        clike.comment.liked = False
        for like in clike.comment.likes:
            if request.user.id == like.user.id:
                clike.comment.liked = True

        recent_activity.append(clike)
    
    recent_activity = sorted(recent_activity, key=lambda x: x.created, reverse=True)
    recent_activity = recent_activity[:3]

    context = { 'posts': filtered_posts, 'post_count': post_count, 'recent_activity': recent_activity }
    
    return render(request, 'base/feed.html', context)

# Single post view (and comment on post)
def post(request, pk):
    post = Post.objects.get(id=pk)

    if request.method == "POST":
        comment = Comment.objects.create(
            author = request.user,
            post = post,
            content = request.POST.get('body')
        )
        post.participants.add(request.user)
        return redirect('post', pk=post.id)

    post.liked = False
    post.commented = False
    post_likes = PostLike.objects.filter(post=post)
    post.likes = post_likes
    for like in post_likes:
        if request.user.id == like.user.id:
            post.liked = True
    comments = Comment.objects.filter(post=post)
    for comment in comments:
        comment_likes = CommentLike.objects.filter(comment=comment)
        comment.likes = comment_likes
        for comment_like in comment_likes:
            if request.user.id == comment_like.user.id:
                comment.liked = True
        if request.user.id == comment.author.id:
            post.commented = True

    post.comments = comments
    participants = post.participants.all()

    if request.method == "POST":
        comment = Comment.objects.create(
            author = request.user,
            post = post,
            content = request.POST.get('body')
        )
        post.participants.add(request.user)
        return redirect('post', pk=post.id)

    context = {'post': post, 'participants': participants}
    return render(request, 'base/post.html', context)

# Create post
@login_required(login_url="/login")
def createPost(request):
    form = PostForm()
    if request.method == 'POST':
        Post.objects.create(
            author=request.user,
            content=request.POST.get('content'),
            edited=False
        )
        return redirect('feed')

    context = {'form': form}
    return render(request, 'base/create-post.html', context)

# Update post
@login_required(login_url="/login")
def updatePost(request, pk):
    post = Post.objects.get(id=pk)
    form = PostForm(instance=post)
    if request.user != post.author:
        return HttpResponse('You are not allowed here!')

    if request.method == 'POST':
        post.content = request.POST.get("content")
        post.edited = True
        post.save()
        return redirect('feed')

    context = {'form': form, "post": post}
    return render(request, 'base/edit-post.html', context)

# Delete post
@login_required(login_url="/login")
def deletePost(request, pk):
    post = Post.objects.get(id=pk)
    likes = PostLike.objects.filter(post=post)
    post.likes = likes
    post.liked = False
    for like in post.likes:
        if request.user.id == like.user.id:
            post.liked = True
    # Get post comments for checks
    comments = Comment.objects.filter(post=post)
    post.comments = comments
    post.commented = False
    for comment in post.comments:
        if request.user.id ==  comment.author.id:
            post.commented = True

    if request.user != post.author:
        return HttpResponse('You are not allowed here!')

    if request.method == 'POST':
        post.delete()
        return redirect('feed')
    
    context = { "post": post }
    return render(request, 'base/delete-post.html', context)

# Like post


# Update comment
@login_required(login_url="/login")
def updateComment(request, pk):
    comment = Comment.objects.get(id=pk)
    post = Post.objects.filter(id=comment.post.id)
    print(comment.post.id)
    form = CommentForm(instance=comment)
    if request.user != comment.author:
        return HttpResponse('You are not allowed here!')

    if request.method == 'POST':
        comment.content = request.POST.get("content")
        comment.edited = True
        comment.save()
        return redirect('post', pk=post.id)

    context = {'form': form, "post": post, "comment": comment}
    return render(request, 'base/edit-comment.html', context)


# Delete comment
@login_required(login_url="/login")
def deleteComment(request, pk):
    comment = Comment.objects.get(id=pk)
    post = Post.objects.get(id=comment.post.id)
    likes = CommentLike.objects.filter(comment=comment)
    comment.likes = likes
    comment.liked = False
    for like in comment.likes:
        if request.user.id == like.user.id:
            comment.liked = True

    if request.user != comment.author:
        return HttpResponse('You are not allowed here!')

    if request.method == 'POST':
        comment.delete()
        return redirect('post', pk=post.id)
    
    context = { "comment": comment, "post": post }
    return render(request, 'base/delete-comment.html', context)

# Like comment

# Profile view
def userProfile(request, pk):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    user = User.objects.get(id=pk)

    user_like_list = []
    recent_activity = []

    # Posts
    posts = Post.objects.filter(
        Q(author=user),
        Q(content__icontains=q)
    )
    post_count = posts.count()
    # PostLikes + comments for posts
    for post in posts:
        post_likes = PostLike.objects.filter(post=post)
        post.likes = post_likes
        post.type = 'post'
        post.shorten = len(post.content) > 20
        strippedContent = post.content[0:20].strip()
        post.shortened = strippedContent + '...'
        post.liked = False
        for like in post.likes:
            if request.user.id == like.user.id:
                post.liked = True
        # Get post comments for checks
        comments = Comment.objects.filter(post=post)
        post.comments = comments
        post.commented = False
        for comment in post.comments:
            if request.user.id ==  comment.author.id:
                post.commented = True
        recent_activity.append(post)
        
    # Comments
    comments = Comment.objects.filter(
        Q(author=user)
    )
    # comment_likes for comments
    for comment in comments:
        comment.type = "comment"
        
        comment_likes = CommentLike.objects.filter(comment=comment)
        comment.likes = comment_likes
        comment.shorten = len(comment.content) > 20
        strippedContent = comment.content[0:20].strip()
        comment.shortened = strippedContent + '...'
        for like in comment_likes:
            if request.user.id == like.user.id:
                comment.liked = True
        # Get like/comment data for commented post
        comment_post_likes = PostLike.objects.filter(post=comment.post)
        comment.post.liked = False
        for like in comment_post_likes:
            if request.user.id == like.user.id:
                comment.post.liked = True
        comment_post_comments = Comment.objects.filter(post=comment.post)
        comment.post.comments = comment_post_comments
        comment.post.commented = False
        for post_comment in comment.post.comments:
            if request.user.id == post_comment.author.id:
                comment.post.commented = True
        recent_activity.append(comment)

    # All likes made by the user
    user_comment_likes = CommentLike.objects.filter(user = user)
    # Like data for liked comment
    for comment_like in user_comment_likes:
        comment  = comment_like.comment
        comment.shorten = len(comment.content) > 20
        strippedContent = comment.content[0:20].strip()
        comment.shortened = strippedContent + '...'
        comment_like.type = 'comment_like'
        comment_likes = CommentLike.objects.filter(comment = comment)
        comment.likes = comment_likes
        for like in comment.likes:
            if request.user.id == like.user.id:
                comment.liked = True
        recent_activity.append(comment_like)
        user_like_list.append(comment_like)

    # Like data for liked post
    user_post_likes = PostLike.objects.filter(user = user)
    for post_like in user_post_likes:
        post  = post_like.post
        post.shorten = len(post.content) > 20
        strippedContent = post.content[0:20].strip()
        post.shortened = strippedContent + '...'
        post_like.type = 'post_like'
        for like in user_post_likes:
            if request.user.id == like.user.id:
                post.liked = True
        post.commented = False
        post_comments = Comment.objects.filter(
            Q(post = post),
        )
        for comment in post_comments:
            if request.user.id ==  comment.author.id:
                post.commented = True
        recent_activity.append(post_like)
        user_like_list.append(post_like)
    
    # Organize recent activity + likes
    recent_activity = sorted(recent_activity, key=lambda x: x.created, reverse=True)
    user_like_list = sorted(user_like_list, key=lambda x: x.created, reverse=True)
    recent_activity = recent_activity[:3]

    # Set and return
    context = {
        "user_profile": user,
        "posts": posts,
        "post_count": post_count,
        "comments": comments,
        "likes": user_like_list,
        "recent_activity": recent_activity
    }
    return render(request, 'base/profile.html', context)

# Edit profile
def updateUser(request):
    user = request.user
    form =  UserForm(instance=user)

    if request.method == "POST":
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            toSave = form.save(commit=False)
            toSave.avatar = request.POST.get('avatar')
            toSave.save()
            return redirect('profile', pk=user.id)
    
    sliced_url = user.avatar.url.split('/images')[1]

    context = {"form": form, "user": user, "sliced_url": sliced_url}
    return render(request, 'base/update-user.html', context)

# Activity View
def activityFeed(request):
    # Concat all recent queries
    recent_activity = []

    # Set all recent post data - done
    # Get dicts
    recent_posts = Post.objects.all()[:3]
    # Get assc models with posts
    for post in recent_posts:
        # Get likes for post
        likes = PostLike.objects.filter(post=post)
        post.likes = likes
        post.type = "post"
        post.shorten = len(post.content) > 20
        strippedContent = post.content[0:20].strip()
        post.shortened = strippedContent + '...'
        post.liked = False
        for like in post.likes:
            if request.user.id == like.user.id:
                post.liked = True
        # Get post comments for checks
        comments = Comment.objects.filter(post=post)
        post.comments = comments
        post.commented = False
        for comment in post.comments:
            if request.user.id ==  comment.author.id:
                post.commented = True
        
        recent_activity.append(post)
    
    # Get all recent likes of posts - 
    recent_post_likes = PostLike.objects.all()[:3]
    for plike in recent_post_likes:
        # Get all likes of liked post
        likes = PostLike.objects.filter(post = plike.post)
        plike.post.likes = likes
        plike.type = "post_like"
        plike.post.shorten = len(plike.post.content) > 20
        strippedContent = plike.post.content[0:20].strip()
        plike.post.shortened = strippedContent + '...'

        # Append like and comment data to dict
        plike.post.liked = False
        for like in plike.post.likes:
            if request.user.id == like.user.id:
                plike.post.liked = True
        # Get post comments for checks
        comments = Comment.objects.filter(post=plike.post)
        plike.post.comments = comments
        plike.post.commented = False
        for comment in plike.post.comments:
            if request.user.id ==  comment.author.id:
                plike.post.commented = True
        
        recent_activity.append(plike)
    
    # Get all recent comments
    recent_comments = Comment.objects.all()[:3]
    for comment in recent_comments:
        # Get all likes of liked comment
        likes = CommentLike.objects.filter(comment = comment)
        comment.likes = likes
        comment.type = 'comment'
        comment.shorten = len(comment.content) > 25
        strippedContent = comment.content[0:25].strip()
        comment.shortened = strippedContent + '...'

        comment.liked = False
        for like in comment.likes:
            if request.user.id == like.user.id:
                comment.liked = True

        recent_activity.append(comment)
    
    # Get all recent likes of comments
    recent_comment_likes = CommentLike.objects.all()[:3]
    for clike in recent_comment_likes:
        # Get all likes of a liked comment
        likes = CommentLike.objects.filter(comment = clike.comment)
        clike.comment.likes = likes
        clike.type = 'comment_like'
        clike.comment.shorten = len(clike.comment.content) > 20
        strippedContent = clike.comment.content[0:20].strip()
        clike.comment.shortened = strippedContent + '...'

        # Append like and comment data to dict
        clike.comment.liked = False
        for like in clike.comment.likes:
            if request.user.id == like.user.id:
                clike.comment.liked = True

        recent_activity.append(clike)
    
    recent_activity = sorted(recent_activity, key=lambda x: x.created, reverse=True)
    recent_activity = recent_activity
    activity_length = len(recent_activity)

    context = { 'recent_activity': recent_activity, "activity_length": activity_length }
    
    return render(request, 'base/activity-component.html', context)