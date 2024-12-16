
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Post, Subscription
from .models import Comment


@receiver(post_save, sender=Post)
def notify_subscribers_on_new_post(sender, instance, created, **kwargs):
    if created:  
        subscribers = Subscription.objects.filter(is_active=True)
        for subscriber in subscribers:
            send_mail(
                subject=f"New Post: {instance.title}",
                message=f"Check out our new post: {instance.title}\n\n{instance.content}",
                from_email='your_email@example.com',
                recipient_list=[subscriber.email],
            )

@receiver(post_save, sender=Comment)
def notify_author_on_comment(sender, instance, created, **kwargs):
    if created:  
        post = instance.post
        author_email = post.author.email
        send_mail(
            subject=f"New Comment on Your Post: {post.title}",
            message=f"{instance.user.username} commented on your post: {instance.content}",
            from_email='your_email@example.com',
            recipient_list=[author_email],
        )