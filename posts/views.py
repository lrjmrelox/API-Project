from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .permissions import IsPostAuthor
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.models import User, Group # built-in user
from rest_framework.authtoken.models import Token
from django.core.cache import cache
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.db.models import Q 
from .models import Post, Comment, Like, admin_required
from .serializers import UserSerializer, PostSerializer, CommentSerializer, LikeSerializer


class FeedPagination(PageNumberPagination):
    page_size = 5


class FeedView(APIView):
    serializer_class = PostSerializer
    pagination_class = FeedPagination

    def get(self, request):
        print(">>> FEEDVIEW IS EXECUTING", flush=True)
        page = request.query_params.get('page', 1)
        cache_key = f"feed_page_{page}"

        # DEBUG LOGS – These will ALWAYS show
        cached_data = cache.get(cache_key)
        if cached_data:
            print(">>> CACHE HIT:", cache_key, flush=True)
            return Response(cached_data)
        
        print(">>> CACHE MISS:", cache_key, flush=True)

        user = request.user

        # Handle anonymous VS authenticated users
        if user.is_authenticated:
            queryset = Post.objects.filter(
                Q(privacy='public') | Q(author=user)
            )
        else:
            queryset = Post.objects.filter(privacy="public")

        # Query optimization
        queryset = queryset.select_related('author') \
                           .prefetch_related('comments', 'likes') \
                           .order_by('-created_at')

        # Pagination
        paginator = FeedPagination()
        result_page = paginator.paginate_queryset(queryset, request)

        serializer = PostSerializer(result_page, many=True)
        response_data = paginator.get_paginated_response(serializer.data).data

        # Store in cache
        cache.set(cache_key, response_data, timeout=60)

        return Response(response_data)
    


class UserListCreate(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username="new_user", password="secure_pass123")

        if role:
            group, created = Group.objects.get_or_create(name=role)
            user.groups.add(group)

        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)



class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check credentials
        user = authenticate(username=username, password=password)
        if user is not None:
            return Response({
                "message": "Login successful",
                "user_id": user.id,
                "username": user.username,
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)



class ObtainAuthTokenView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key})
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)



class PostListCreate(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        posts = Post.objects.filter(
       Q(privacy='public') | Q(author=request.user)
    ).order_by('-created_at')
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentListCreate(APIView):
    def get(self, request):
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetailView(APIView):
    permission_classes = [IsAuthenticated, IsPostAuthor]

    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)

        if post.privacy == 'private' and post.author != request.user:
            return Response({"error": "Provate post"}, status=403)
        
        self.check_object_permissions(request, post)
        serializer = PostSerializer(post)
        return Response(serializer.data)


class DeletePost(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        post = get_object_or_404(Post, pk=pk)

        # Only admins can delete posts
        if not request.user.is_superuser and request.user.groups.filter(name='admin').exists() == False:
            return Response({"error": "Admin access required to delete posts"}, status=403)

        post.delete()
        return Response({"message": "Post deleted"}, status=200)
    

class ProtectedView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


    def get(self, request):
        return Response({"message": "Authenticated!"})
    


class LikePost(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        post = get_object_or_404(Post, id=id)

        like, created = Like.objects.get_or_create(
            user=request.user,
            post=post
        )

        if not created:
            return Response({"error": "You already liked this post."}, status=400)

        serializer = LikeSerializer(like)
        return Response(serializer.data, status=201)



class CommentPost(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        post = get_object_or_404(Post, id=id)

        text = request.data.get("text")
        if not text:
            return Response({"error": "Comment text cannot be empty."}, status=400)

        comment = Comment.objects.create(
            text=text,
            author=request.user,
            post=post
        )

        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=201)


class GetComments(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        post = get_object_or_404(Post, id=id)
        comments = Comment.objects.filter(post=post).order_by('-created_at')

        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)


class PostLikesCount(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id):
        post = get_object_or_404(Post, id=id)
        like_count = post.likes.count()
        return Response({"likes": like_count})