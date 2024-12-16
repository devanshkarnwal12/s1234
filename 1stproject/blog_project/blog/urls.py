from django.urls import path
from django.contrib.auth import views as auth_views  
from . import views
from .views import LoginAPIView, LogoutAPIView, UserRegistrationAPIView,CommentListCreateAPIView, CommentDetailAPIView, CurrentUserAPIView, GetAllUsersAPIView, GetUserByIdAPIView, UpdateUserProfileAPIView, DeleteUserAPIView, CreatePostView, PostListAPIView, PostDetailAPIView, PostUpdateAPIView, PostDeleteAPIView, CommentCreateAPIView, PostCommentsAPIView,CommentListAPIView, CommentDeleteAPIView, CategoryCreateAPIView, CategoryListAPIView,CategoryUpdateAPIView, CategoryDeleteAPIView, TagCreateAPIView, TagListAPIView, TagDeleteAPIView, PostSearchAPIView, LikePostAPIView, FeaturedPostListAPIView, CreatePostAPIView





urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),  # Corrected: removed redundant path
    path('register/', UserRegistrationAPIView.as_view(), name='user-registration'),
    path('profile/', views.profile, name='profile'),
    path('category/<int:category_id>/', views.posts_by_category, name='posts_by_category'),
    path('tag/<int:tag_id>/', views.posts_by_tag, name='posts_by_tag'),
    path('post/<int:post_id>/like/', views.like_post, name='like_post'),  # Corrected: use post_id for consistency
    path('search/', views.post_search, name='post_search'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),  
    path('subscribe/', views.subscribe, name='subscribe'),
    path('success/', views.success, name='success'),
    path('bookmark/<int:post_id>/', views.toggle_bookmark, name='toggle_bookmark'),
    path('bookmarked/', views.bookmarked_posts, name='bookmarked_posts'),
    path('dark-mode/', views.dark_mode_view, name='dark_mode'),  # URL for dark mode page
    path('recent-posts/', views.recent_posts, name='recent_posts'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('question-solution-form/', views.question_solution_form, name='question_solution_form'),
    # Optionally, add a list view for all questions and solutions
    path('question-solution-list/', views.question_solution_list, name='question_solution_list'),
    path('', views.homepage, name='homepage'),
    path('toggle_featured/<int:pk>/', views.toggle_featured, name='toggle_featured'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('api/comments/', CommentListCreateAPIView.as_view(), name='comment-list-create'),
    path('api/comments/<int:pk>/', CommentDetailAPIView.as_view(), name='comment-detail'),
    path('api/current-user/', CurrentUserAPIView.as_view(), name='current_user'),
    path('api/users/', GetAllUsersAPIView.as_view(), name='get_all_users'),
    path('api/users/<int:user_id>/', GetUserByIdAPIView.as_view(), name='get_user_by_id'),
    path('api/profile/update/', UpdateUserProfileAPIView.as_view(), name='update_user_profile'),
    path('api/users/<int:user_id>/delete/', DeleteUserAPIView.as_view(), name='delete_user'),
    path('create/', CreatePostView.as_view(), name='create_post'),
    path('posts/', PostListAPIView.as_view(), name='post-list'),
    path('posts/<int:pk>/', PostDetailAPIView.as_view(), name='post-detail'),
    path('posts/<int:id>/update/', PostUpdateAPIView.as_view(), name='post-update'),
    path('posts/<int:pk>/delete/', PostDeleteAPIView.as_view(), name='post-delete'),
    path('posts/<int:post_id>/comments/', CommentCreateAPIView.as_view(), name='comment-create'),
    path('posts/<int:pk>/comments/', PostCommentsAPIView.as_view(), name='post-comments'),
    path('posts/<int:post_id>/comments/', CommentListAPIView.as_view(), name='comment-list'),
    path('comments/<int:pk>/delete/', CommentDeleteAPIView.as_view(), name='comment-delete'),
    path('categories/create/', CategoryCreateAPIView.as_view(), name='category-create'),
    path('categories/', CategoryListAPIView.as_view(), name='category-list'),
    path('categories/<int:id>/update/', CategoryUpdateAPIView.as_view(), name='category-update'),
    path('categories/<int:id>/delete/', CategoryDeleteAPIView.as_view(), name='category-delete'),
    path('tags/create/', TagCreateAPIView.as_view(), name='tag-create'),
    path('tags/', TagListAPIView.as_view(), name='tag-list'), 
    path('tags/<int:id>/delete/', TagDeleteAPIView.as_view(), name='tag-delete'),
    path('posts/search/', PostSearchAPIView.as_view(), name='post-search'),
    path('posts/<int:post_id>/like/', LikePostAPIView.as_view(), name='like-post'),
    path('posts/featured/', FeaturedPostListAPIView.as_view(), name='featured-posts'),
    path('posts/create/', CreatePostAPIView.as_view(), name='create-post'),
]

