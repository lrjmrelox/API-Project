from django.urls import path
from .views import UserListCreate, LoginView, ObtainAuthTokenView, PostListCreate, CreatePostView, CommentListCreate



urlpatterns = [
    path('users/register/', UserListCreate.as_view(), name='user-list-create'),
    path('login/', LoginView.as_view(), name='login'),
    path('api/token/', ObtainAuthTokenView.as_view(), name='api-token'),
    path('posts/', PostListCreate.as_view(), name='post-list-create'),
    path('comments/', CommentListCreate.as_view(), name='comment-list-create'),
    path('posts/create-factory/', CreatePostView.as_view(), name='create_post_factory'),
]
