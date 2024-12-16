from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from ckeditor.fields import RichTextField
from django import forms
from django.utils.text import slugify

# Category Model
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

# Tag Model
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        while Tag.objects.filter(slug=self.slug).exists():
            self.slug = slugify(f"{self.name}-{self.pk}")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

# Post Model
class Post(models.Model):
    title = models.CharField(max_length=200)
    content = RichTextField()  
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='posts')
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='posts')
    share_count = models.PositiveIntegerField(default=0)  
    views_count = models.PositiveIntegerField(default=0)
    published_date = models.DateTimeField(default=timezone.now)
    is_featured = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    DRAFT = 'draft'
    PUBLISHED = 'published'
    STATUS_CHOICES = [
        (DRAFT, 'Draft'),
        (PUBLISHED, 'Published'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=DRAFT)

    def __str__(self):
        return self.title

    def total_likes(self):
        return self.likes.count()

    def total_shares(self):
        return self.share_count

    def increment_share_count(self):
        self.share_count += 1
        self.save()

    def increment_views(self):
        self.views_count += 1
        self.save()

    @classmethod
    def search(cls, query):
        search_query = SearchQuery(query)
        return cls.objects.annotate(
            search=SearchVector('title', 'content', 'author__username'),
            rank=SearchRank(SearchVector('title', 'content', 'author__username'), search_query)
        ).filter(search=search_query).order_by('-rank')

# Profile Model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True)
    social_link = models.URLField(blank=True)
    bookmarked_posts = models.ManyToManyField(Post, blank=True, related_name='bookmarked_by')

    def __str__(self):
        return f'{self.user.username} Profile'

@receiver(post_save, sender=User)
def create_or_save_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()

# Comment Model
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name="replies")
    approved = models.BooleanField(default=False)  

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.title}"

    class Meta:
        ordering = ['created_at']

# Subscription Model
class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="subscriptions")
    email = models.EmailField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s subscription"

    class Meta:
        ordering = ['-created_at']

# Post Form
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'tags', 'status']

# Bookmark Model
class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    bookmarked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f"Bookmark {self.id} for {self.user.username} - {self.post.title}"

# QuestionSolution Model
class QuestionSolution(models.Model):
    question = models.CharField(max_length=255)
    solution = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.question
    
    class Meta:
        ordering = ['created_at']

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')  # Add related_name here
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} likes {self.post}"
