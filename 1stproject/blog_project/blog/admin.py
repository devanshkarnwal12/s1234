from django.contrib import admin
from django.contrib.auth.models import User
from .models import Post, Profile, Category, Tag, Comment

# Register Category and Tag
admin.site.register(Category)
admin.site.register(Tag)


# Post Admin Customization
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'created_at', 'total_likes', 'total_shares', 'total_comments', 'published_date','is_featured']
    list_filter = ['category', 'created_at', 'author','is_featured']
    search_fields = ['title', 'content', 'author__username']
    actions = ['increment_share_count', 'reset_share_count']
    
    def total_comments(self, obj):
        return obj.comments.count()
    
    def total_likes(self, obj):
        return obj.likes.count()

    def total_shares(self, obj):
        return obj.share_count

    def increment_share_count(self, request, queryset):
        for post in queryset:
            post.increment_share_count()
    increment_share_count.short_description = "Increment share count for selected posts"
    
    def reset_share_count(self, request, queryset):
        queryset.update(share_count=0)
    reset_share_count.short_description = "Reset share count for selected posts"

admin.site.register(Post, PostAdmin)


# Profile Admin Customization
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'bio', 'profile_image', 'social_link']
    search_fields = ['user__username', 'bio']

admin.site.register(Profile, ProfileAdmin)


# Comment Admin Customization
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at', 'approved', 'parent']
    list_filter = ['approved', 'created_at']
    search_fields = ['content']
    actions = ['approve_comments', 'delete_comments']

    def approve_comments(self, request, queryset):
        queryset.update(approved=True)
    approve_comments.short_description = "Mark selected comments as approved"

    def delete_comments(self, request, queryset):
        queryset.delete()
    delete_comments.short_description = "Delete selected comments"

admin.site.register(Comment, CommentAdmin)


# User Management: Customizing User Admin
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_active', 'date_joined', 'total_likes')
    actions = ['ban_user']

    def total_likes(self, obj):
        return obj.liked_posts.count()
    total_likes.short_description = "Total Likes"

    def ban_user(self, request, queryset):
        queryset.update(is_active=False)
    ban_user.short_description = "Ban selected users"

# Unregister the default User admin and register the custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
