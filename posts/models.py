from django.db import models
from django.contrib.auth.models import User, Group, Permission
from rest_framework.response import Response


class Post(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    privacy = models.CharField(
        max_length=7,
        choices=[('public', 'Public'), ('private', 'Private')],
        default='public'
    )
    created_at = models.DateTimeField(auto_now_add=True)

def admin_required(func):
    def wrapper(request, *args, **kwargs):
        if not request.user.groups.filter(name='admin').exists():
            return Response({'error': 'Admin access required'}, status=403)
        return func(request, *args, **kwargs)
    return wrapper


class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on Post {self.post.id}"


class Like(models.Model):
    user = models.ForeignKey(User, related_name='likes', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f"{self.user.username} liked Post {self.post.id}"