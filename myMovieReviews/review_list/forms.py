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

        labels = {
            "title": "제목",
            "release_year": "개봉년도",
            "director": "감독",
            "actors": "주연",
            "genre": "장르",
            "rating": "별점",
            "running_time": "러닝타임",
            "review_content": "리뷰",
        }