from django.contrib import admin
from .models import Post, Comment, Story, StoryImage, Profile
from .models import Follow

admin.site.register(Post)
admin.site.register(Profile)
admin.site.register(Follow)
