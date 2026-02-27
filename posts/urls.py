from django.urls import path
from .views import UserListCreate, LoginView, ObtainAuthTokenView, PostListCreate, CommentListCreate, LikePost, CommentPost, GetComments, PostLikesCount



urlpatterns = [
    path('users/register/', UserListCreate.as_view(), name='user-list-create'),
    path('login/', LoginView.as_view(), name='login'),
    path('api/token/', ObtainAuthTokenView.as_view(), name='api-token'),
    path('posts/', PostListCreate.as_view(), name='post-list-create'),
    path('comments/', CommentListCreate.as_view(), name='comment-list-create'),
    path("posts/<int:id>/like/", LikePost.as_view(), name="like-post"),
    path("posts/<int:id>/comment/", CommentPost.as_view(), name="comment-post"),
    path("posts/<int:id>/comments/", GetComments.as_view(), name="get-comments"),
    path("posts/<int:id>/likes/", PostLikesCount.as_view(), name="post-likes")
]
