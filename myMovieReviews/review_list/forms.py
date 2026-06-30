from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            "title",
            "release_year",
            "director",
            "actors",
            "genre",
            "rating",
            "running_time",
            "review_content",
        ]