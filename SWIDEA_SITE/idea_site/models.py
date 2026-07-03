from django.conf import settings
from django.db import models


class DevTool(models.Model):
    name = models.CharField(max_length=50)
    kind = models.CharField(max_length=50)
    content = models.TextField()

    def __str__(self):
        return self.name


class Idea(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='ideas/', blank=True, null=True)
    content = models.TextField()
    interest = models.IntegerField(default=0)
    devtool = models.ForeignKey(
        DevTool,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ideas'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def star_count(self):
        return self.stars.count()

    def __str__(self):
        return self.title


class IdeaStar(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, related_name='stars')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'idea')

    def __str__(self):
        return f'{self.user} - {self.idea}'