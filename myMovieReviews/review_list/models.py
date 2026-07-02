from django.db import models

class Post(models.Model):
    title = models.CharField(max_length=200)
    release_year = models.IntegerField()
    director = models.CharField(max_length=100)
    actors = models.CharField(max_length=300)
    genre = models.CharField(max_length=200)
    rating = models.FloatField()
    running_time = models.IntegerField()
    review_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title