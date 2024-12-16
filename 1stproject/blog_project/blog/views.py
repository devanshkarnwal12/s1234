from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Post, Category, Tag, Comment, Subscription, Bookmark, Profile, QuestionSolution, Like
from .forms import UserRegistrationForm, ProfileForm, CommentForm, PostForm, SubscriptionForm, QuestionSolutionForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages  
from django.core.mail import send_mail
from django.conf import settings
from .models import QuestionSolution
from .forms import QuestionSolutionForm
from django.db import migrations, models
import django.utils.timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.generics import UpdateAPIView, DestroyAPIView, ListAPIView
from rest_framework.exceptions import NotFound
from rest_framework import generics, status
from .serializers import CommentSerializer, CategorySerializer, TagSerializer, PostSerializer, LikeSerializer
from rest_framework.filters import SearchFilter
from .models import Like, Post
from rest_framework.exceptions import ValidationError


from .models import (
    Post, Category, Tag, Comment, Subscription,
    Bookmark, Profile, QuestionSolution
)
from .forms import (
    UserRegistrationForm, ProfileForm, CommentForm,
    PostForm, SubscriptionForm, QuestionSolutionForm
)
from .serializers import (
    UserRegistrationSerializer, CommentSerializer,
    CurrentUserSerializer, UserSerializer, UpdateUserProfileSerializer, PostSerializer
)

from django.contrib.auth import authenticate

# Admin Dashboard
@login_required
def admin_dashboard(request):
    try:
        post_count = Post.objects.count()
        total_comments = Comment.objects.count()
        total_likes = Post.objects.aggregate(total_likes=Count('likes'))
        user_count = User.objects.count()

        return render(request, 'admin/dashboard.html', {
            'post_count': post_count,
            'total_comments': total_comments,
            'total_likes': total_likes.get('total_likes', 0),
            'user_count': user_count,
        })
    except Exception as e:
        return render(request, 'admin/dashboard.html', {'error': str(e)})


# List of all posts with categories and tags for filtering and pagination
def post_list(request):
    try:
        posts = Post.objects.filter(status='published', published_date__lte=timezone.now()).order_by('-published_date')  
        categories = Category.objects.all()
        tags = Tag.objects.all()

        paginator = Paginator(posts, 10)  
        page_number = request.GET.get('page')
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        return render(request, 'blog/post_list.html', {
            'page_obj': page_obj,
            'categories': categories,
            'tags': tags,
        })
    except Exception as e:
        return render(request, 'blog/post_list.html', {'error': str(e)})


# About page view
def about(request):
    return render(request, 'blog/about.html')


# Filter posts by category
def posts_by_category(request, category_id):
    try:
        category = get_object_or_404(Category, id=category_id)
        posts = Post.objects.filter(category=category)
        return render(request, 'blog/posts_by_category.html', {'posts': posts, 'category': category})
    except Exception as e:
        return render(request, 'blog/posts_by_category.html', {'error': str(e)})


# Filter posts by tag
def posts_by_tag(request, tag_id):
    try:
        tag = get_object_or_404(Tag, id=tag_id)
        posts = Post.objects.filter(tags=tag)
        return render(request, 'blog/posts_by_tag.html', {'posts': posts, 'tag': tag})
    except Exception as e:
        return render(request, 'blog/posts_by_tag.html', {'error': str(e)})


# View for post details and handling comments
def post_detail(request, post_id):
    try:
        post = get_object_or_404(Post, id=post_id)
        post.views_count += 1
        post.save(update_fields=['views_count'])

        # Handle comments
        if request.method == "POST":
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.post = post
                comment.user = request.user
                parent_id = request.POST.get("parent")
                if parent_id:
                    comment.parent = Comment.objects.get(id=parent_id)
                comment.save()

                # Send email notification to post author
                post_author = post.author
                send_mail(
                    subject=f'New comment on your post: {post.title}',
                    message=f'{request.user.username} commented on your post: {post.title}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[post_author.email],
                )
                return redirect('post_detail', post_id=post.id)
        else:
            form = CommentForm()

        comments = post.comments.filter(parent__isnull=True)
        replies = post.comments.filter(parent__isnull=False)

        # Find related posts by tags
        related_posts = Post.objects.filter(tags__in=post.tags.all()).exclude(id=post.id).distinct()

        return render(request, 'blog/post_detail.html', {
            'post': post,
            'comments': comments,
            'form': form,
            'replies': replies,
            'related_posts': related_posts,
        })
    except Exception as e:
        return render(request, 'blog/post_detail.html', {'error': str(e)})


class CommentListCreateAPIView(APIView):
    def get(self, request):
        try:
            comments = Comment.objects.all()
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': f'Error fetching comments: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = CommentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'Error creating comment: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class CommentDetailAPIView(APIView):
    def get(self, request, pk):
        try:
            comment = get_object_or_404(Comment, pk=pk)
            serializer = CommentSerializer(comment)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': f'Error fetching comment with ID {pk}: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        try:
            comment = get_object_or_404(Comment, pk=pk)
            serializer = CommentSerializer(comment, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'Error updating comment with ID {pk}: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        try:
            comment = get_object_or_404(Comment, pk=pk)
            comment.delete()
            return Response({'message': 'Comment deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': f'Error deleting comment with ID {pk}: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserRegistrationAPIView(APIView):
    def post(self, request):
        try:
            serializer = UserRegistrationSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"message": "User registered successfully."},
                    status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'Error registering user: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Contact page view
def contact(request):
    return render(request, 'blog/contact.html')


# User profile view
@login_required
def profile(request):
    try:
        if request.method == 'POST':
            profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
            if profile_form.is_valid():
                profile_form.save()
                return redirect('profile')
        else:
            profile_form = ProfileForm(instance=request.user.profile)
        return render(request, 'blog/profile.html', {'profile_form': profile_form})
    except Exception as e:
        return render(request, 'blog/profile.html', {'error': str(e)})


# Like and Unlike Post
@login_required
def like_post(request, post_id):
    try:
        post = get_object_or_404(Post, id=post_id)
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)
        return JsonResponse({'total_likes': post.likes.count()})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Search posts by title, content, or author
def post_search(request):
    query = request.GET.get('q', '')
    posts = Post.objects.all()

    if query:
        posts = posts.filter(
            Q(title__icontains=query) | Q(content__icontains=query) | Q(author__username__icontains=query)
        )

    return render(request, 'blog/post_search.html', {'posts': posts, 'query': query})

# Create Post view with form handling for file uploads
@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            return redirect('post_detail', post_id=post.id)
    else:
        form = PostForm()
    return render(request, 'create_post.html', {'form': form})

# Edit Post view
@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            if post.published_date > timezone.now() and post.status == 'published':
                messages.info(request, 'Your post is scheduled for future publication.')
            post.save()
            messages.success(request, 'Post updated successfully!')
            return redirect('post_detail', post_id=post.id)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/edit_post.html', {'form': form, 'post': post})

# Subscribe to the blog
def subscribe(request):
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            form.save()

            # Send subscription confirmation email
            send_mail(
                subject='Blog Subscription Confirmation',
                message='Thank you for subscribing to our blog! You will now receive updates about new posts.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[form.cleaned_data['email']],
            )

            messages.success(request, 'You have successfully subscribed to the blog!')
            return redirect('blog:subscribe')
    else:
        form = SubscriptionForm()
    return render(request, 'blog/subscribe.html', {'form': form})

# Success page view after subscription
def success(request):
    return render(request, 'blog/success.html')

# Toggle bookmark for a post
@login_required
def toggle_bookmark(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, post=post)
    if not created:
        bookmark.delete()  # If bookmark already exists, delete it (i.e., unlike)
    return redirect('post_detail', post_id=post_id)

# View for bookmarked posts
@login_required
def bookmarked_posts(request):
    bookmarks = Bookmark.objects.filter(user=request.user)
    posts = [bookmark.post for bookmark in bookmarks]
    return render(request, 'blog/bookmarked_posts.html', {'posts': posts})

# View for dark mode page
def dark_mode_view(request):
    return render(request, 'blog/dark_mode.html')  # You can replace the template name with your own

# View for recent posts
def recent_posts(request):
    recent_posts = Post.objects.all().order_by('-created_at')[:5]
    return render(request, 'blog/recent_posts.html', {'recent_posts': recent_posts})

# Handle Question and Solution form
def question_solution_form(request):
    if request.method == 'POST':
        form = QuestionSolutionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('question_solution_list')  # Redirect to a success page or list
    else:
        form = QuestionSolutionForm()
    return render(request, 'blog/question_solution_form.html', {'form': form})

# List all question solutions
def question_solution_list(request):
    solutions = QuestionSolution.objects.all()
    return render(request, 'blog/question_solution_list.html', {'solutions': solutions})

def set_created_at(apps, schema_editor):
    QuestionSolution = apps.get_model('blog', 'QuestionSolution')
    for solution in QuestionSolution.objects.all():
        if not solution.created_at:
            solution.created_at = django.utils.timezone.now()
            solution.save()

class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0016_previous_migration'),  # adjust this based on your actual previous migration
    ]

    operations = [
        migrations.AddField(
            model_name='questionsolution',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.RunPython(set_created_at, reverse_code=migrations.RunPython.noop),  # sets created_at if missing
    ]

def homepage(request):
    featured_posts = Post.objects.filter(is_featured=True)
    posts = Post.objects.all()  # For other posts

    return render(request, 'homepage.html', {
        'featured_posts': featured_posts,
        'posts': posts,
    })    


def toggle_featured(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    if request.method == 'POST':
        # Check if the post is authored by the current user (if required)
        if post.user == request.user:
            post.is_featured = not post.is_featured
            post.save()
        
        return redirect('post_detail', pk=post.pk)

    return render(request, 'post_detail.html', {'post': post})

# Login API View
class LoginAPIView(APIView):
    def post(self, request):
     try:
        username = request.data.get('username')
        password = request.data.get('password')

        # Authenticate user
        user = authenticate(username=username, password=password)
        if user is not None:
            # Generate JWT tokens (Refresh and Access tokens)
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            return Response({
                'msg': "login succesfully",
                'token':access_token,
            
            }, status=status.HTTP_200_OK)
        else:
           return Response({'status': 'failed', 'msg': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)

        
     except Exception as e:
        return Response({'Error is find': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
# Logout API View
class LogoutAPIView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            token = RefreshToken(refresh_token)

            # Blacklist the token
            token.blacklist()

            return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f'Invalid refresh token: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        

class CurrentUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            serializer = CurrentUserSerializer(request.user)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': f'Error fetching user details: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetAllUsersAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        try:
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f'Error fetching users: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetUserByIdAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            user = get_object_or_404(User, id=user_id)
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f'Error fetching user with ID {user_id}: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateUserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        try:
            user = request.user
            serializer = UpdateUserProfileSerializer(user, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Profile updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': f'Error updating profile: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteUserAPIView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return Response(
                {"message": f"User with ID {user_id} deleted successfully."},
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            return Response(
                {"error": f"User with ID {user_id} does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {'error': f'Error deleting user with ID {user_id}: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class CreatePostView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure user authentication

    def post(self, request):
        data = request.data.copy()
        data['user'] = request.user.id  # Add the authenticated user ID to the data
        serializer = PostSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class PostListAPIView(APIView):
    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)    
    
class PostDetailAPIView(APIView):
    def get(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
            serializer = PostSerializer(post)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response(
                {"error": "Post not found."},
                status=status.HTTP_404_NOT_FOUND
            )    

class PostUpdateAPIView(generics.UpdateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]  # Optional: Only authenticated users can update posts
    lookup_field = 'id'  # Use 'id' as the URL parameter

    def perform_update(self, serializer):
        # You can add any additional logic before saving the updated post here
        serializer.save()


class PostDeleteAPIView(DestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]  # Optional, use if you need authentication

    def perform_destroy(self, instance):
        # You can add any custom logic here if needed before deleting
        instance.delete()      

class CommentCreateAPIView(generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]  # Require authentication to add a comment

    def perform_create(self, serializer):
        # Automatically assign the logged-in user as the author of the comment
        serializer.save(user=self.request.user)     

class PostCommentsAPIView(APIView):
    def get(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
            comments = Comment.objects.filter(post=post)
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)
        except Post.DoesNotExist:
            return Response({"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND)



class CommentListAPIView(ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated (Optional)

    def get_queryset(self):
        post_id = self.kwargs['post_id']  # Get the post ID from the URL
        return Comment.objects.filter(post__id=post_id)
    

class CommentDeleteAPIView(APIView):
    def delete(self, request, pk):
        try:
            comment = Comment.objects.get(pk=pk)
            comment.delete()
            return Response({"message": "Comment deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Comment.DoesNotExist:
            return Response({"error": "Comment not found."}, status=status.HTTP_404_NOT_FOUND)    
        

class CategoryCreateAPIView(generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer   

class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all()  # Retrieve all categories from the database
    serializer_class = CategorySerializer         

class CategoryUpdateAPIView(generics.UpdateAPIView):
    queryset = Category.objects.all()  # Get all categories
    serializer_class = CategorySerializer  # Use CategorySerializer to validate and serialize the data
    lookup_field = 'id'  # Use the 'id' field as the lookup field to find the category

    def perform_update(self, serializer):
        # This method is called to save the updated category instance
        category = serializer.save()     

class CategoryDeleteAPIView(generics.DestroyAPIView):
    queryset = Category.objects.all()  # Query the Category model
    serializer_class = CategorySerializer  # Use CategorySerializer to validate the data
    lookup_field = 'id'        


class TagCreateAPIView(generics.CreateAPIView):
    queryset = Tag.objects.all()  # Querying all tags (although only one will be created)
    serializer_class = TagSerializer

class TagListAPIView(generics.ListAPIView):
    queryset = Tag.objects.all()  # Retrieve all tags from the database
    serializer_class = TagSerializer    

class TagDeleteAPIView(generics.DestroyAPIView):
    queryset = Tag.objects.all()  # Select the Tag model
    serializer_class = TagSerializer  # Optional, for validation and response structure
    lookup_field = 'id'    

class PostSearchAPIView(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    filter_backends = (SearchFilter,)
    search_fields = ['title', 'content', 'category__name']      

class LikePostAPIView(generics.CreateAPIView):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can like a post

    def perform_create(self, serializer):
        user = self.request.user
        post_id = self.kwargs['post_id']
        
        # Check if the post exists
        post = get_object_or_404(Post, id=post_id)  # Efficient way to get the post

        # Check if the user has already liked the post
        if Like.objects.filter(user=user, post=post).exists():
            raise ValidationError("You have already liked this post.")  # Correct use of ValidationError

        # Create the like
        serializer.save(user=user, post=post)
        
        return Response({"message": "Post liked successfully."}, status=status.HTTP_201_CREATED)

class FeaturedPostListAPIView(generics.ListAPIView):
    queryset = Post.objects.filter(is_featured=True)  # Get all featured posts
    serializer_class = PostSerializer


class CreatePostAPIView(generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer    