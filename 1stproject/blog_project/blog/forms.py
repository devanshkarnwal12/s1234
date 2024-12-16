from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile
from .models import Comment
from .models import Post
from ckeditor.widgets import CKEditorWidget
from .models import Subscription
from .models import QuestionSolution

# User Registration Form
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

# Profile Form
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'profile_image', 'social_link']   

# Comment Form
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

    def __init__(self, *args, **kwargs):
        post = kwargs.get('post')
        super().__init__(*args, **kwargs)
        self.fields['content'].widget.attrs['placeholder'] = "Add a comment"
        self.instance.post = post

# Post Form (with CKEditor for content)
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'tags', 'status'] 


class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['email']

def clean_email(self):
        email = self.cleaned_data.get('email')
        if Subscription.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already subscribed.')
        return email



class QuestionSolutionForm(forms.ModelForm):
    class Meta:
        model = QuestionSolution
        fields = ['question', 'solution']
        widgets = {
            'solution': forms.Textarea(attrs={'rows': 5, 'cols': 40}),
        }


        