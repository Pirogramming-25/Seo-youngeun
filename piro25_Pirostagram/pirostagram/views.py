from django.shortcuts import render, redirect, get_object_or_404
from .forms import PostForm
from .models import Post, Comment, Story, StoryImage, Profile, Follow
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.db.models import Q


@login_required
def feed(request):
    following_ids = list(
        Follow.objects.filter(
            follower=request.user
        ).values_list("following_id", flat=True)
    )
    #내 게시글까지 보이게끔
    visible_user_ids = following_ids + [request.user.id]

    posts = Post.objects.filter(
        author_id__in=visible_user_ids
    ).order_by("-created_at")

    stories = Story.objects.filter(
        author_id__in=visible_user_ids
    ).order_by("-created_at")

    return render(request, "pirostagram/feed.html", {
        "posts": posts,
        "stories": stories,
    })


@login_required
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("pirostagram:feed")
    else:
        form = PostForm()

    return render(request, "pirostagram/post_form.html", {"form": form})


def post_update(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)

        if form.is_valid():
            form.save()
            return redirect("pirostagram:feed")
    else:
        form = PostForm(instance=post)

    return render(request, "pirostagram/post_form.html", {
        "form": form,
        "post": post,
    })


@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == "POST":
        post.delete()

    return redirect("pirostagram:feed")


@login_required
@require_POST
def post_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True

    return JsonResponse({
        "liked": liked,
        "like_count": post.likes.count(),
    })


@login_required
@require_POST
def comment_create(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    content = request.POST.get("content")

    if not content:
        return JsonResponse({"error": "댓글 내용을 입력해주세요."}, status=400)

    comment = Comment.objects.create(
        post=post,
        author=request.user,
        content=content,
    )

    return JsonResponse({
        "id": comment.id,
        "author": comment.author.username,
        "content": comment.content,
    })


@login_required
@require_POST
def comment_update(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)
    content = request.POST.get("content")

    if not content:
        return JsonResponse({"error": "댓글 내용을 입력해주세요."}, status=400)

    comment.content = content
    comment.save()

    return JsonResponse({
        "id": comment.id,
        "content": comment.content,
    })


@login_required
@require_POST
def comment_delete(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)
    comment.delete()

    return JsonResponse({
        "deleted": True,
    })


@login_required
def story_create(request):
    if request.method == "POST":
        images = request.FILES.getlist("images")

        if images:
            story = Story.objects.create(author=request.user)

            for image in images:
                StoryImage.objects.create(story=story, image=image)

            return redirect("pirostagram:feed")

    return render(request, "pirostagram/story_form.html")


@login_required
def user_search(request):
    query = request.GET.get("q", "")
    users = []

    if query:
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(profile__name__icontains=query)
        ).exclude(id=request.user.id)

    following_ids = Follow.objects.filter(
        follower=request.user
    ).values_list("following_id", flat=True)

    return render(request, "pirostagram/user_search.html", {
        "query": query,
        "users": users,
        "following_ids": following_ids,
    })


@login_required
def user_profile(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)
    posts = Post.objects.filter(author=profile_user).order_by("-created_at")

    is_following = Follow.objects.filter(
        follower=request.user,
        following=profile_user,
    ).exists()

    follower_count = profile_user.follower_set.count()
    following_count = profile_user.following_set.count()

    return render(request, "pirostagram/user_profile.html", {
        "profile_user": profile_user,
        "posts": posts,
        "is_following": is_following,
        "follower_count": follower_count,
        "following_count": following_count,
    })


@login_required
@require_POST
def follow_toggle(request, user_id):
    target_user = get_object_or_404(User, id=user_id)

    if target_user == request.user:
        return JsonResponse({"error": "자기 자신은 팔로우할 수 없습니다."}, status=400)

    follow = Follow.objects.filter(
        follower=request.user,
        following=target_user,
    )

    if follow.exists():
        follow.delete()
        is_following = False
    else:
        Follow.objects.create(
            follower=request.user,
            following=target_user,
        )
        is_following = True

    follower_count = target_user.follower_set.count()

    return JsonResponse({
        "is_following": is_following,
        "follower_count": follower_count,
    })