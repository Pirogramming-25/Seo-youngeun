from django.urls import path
from . import views

app_name = "pirostagram"

urlpatterns = [
    path("", views.feed, name="feed"),
    path("posts/create/", views.post_create, name="post_create"),
    path("posts/<int:post_id>/edit/", views.post_update, name="post_update"),
    path("posts/<int:post_id>/delete/", views.post_delete, name="post_delete"),
    path("posts/<int:post_id>/like/", views.post_like, name="post_like"),
    path("posts/<int:post_id>/comments/create/", views.comment_create, name="comment_create"),
    path("comments/<int:comment_id>/update/", views.comment_update, name="comment_update"),
    path("comments/<int:comment_id>/delete/", views.comment_delete, name="comment_delete"),
    path("stories/create/", views.story_create, name="story_create"),
    path("users/search/", views.user_search, name="user_search"),
    path("users/<int:user_id>/", views.user_profile, name="user_profile"),
    path("users/<int:user_id>/follow/", views.follow_toggle, name="follow_toggle"),
]