from django.db import models
from django.db.models import Sum
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        print("Extra Fields:", extra_fields)  # Print extra_fields
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

def validate_file_size(value):
    # Max file size in bytes (5MB in this example)
    max_size = 1 * 1024 * 1024  # 5MB

    if value.size > max_size:
        raise ValidationError('File size cannot exceed 1MB.')

class CustomUser(AbstractBaseUser):  # Renamed to CustomUser
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    signature = models.TextField(blank=True)
    country = models.TextField(blank=True)
    age = models.IntegerField(default=0)
    gender = models.TextField(blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    display_gender = models.BooleanField(default=True) 
    display_age = models.BooleanField(default=True)   
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    profile_picture = models.ImageField(
        upload_to='profile_pics/', 
        blank=True, 
        null=True, 
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']), validate_file_size]
    )
    picture_url = models.URLField(blank=True, null=True)
    reputation_points = models.IntegerField(default=0)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    def save(self, *args, **kwargs):
        # Ensure bio field is updated before saving
        self.bio = self.bio.strip()  # Strip any leading/trailing whitespace
        super().save(*args, **kwargs)

    def has_module_perms(self, app_label):
        # Implement your permissions logic here
        return True 

    def has_perm(self, perm, obj=None):
        """
        Does the user have a specific permission?
        """
        # For simplicity, you can return True for all permissions
        return True
    
    def update_reputation_points(self):
        votes = Vote.objects.filter(post__user_id=self)
        self.reputation_points = votes.aggregate(total=Sum('value'))['total'] or 0
        self.save()

class Section(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
class Thread(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_DEFAULT, default=12)
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    views = models.IntegerField(default=0)
    user_id = models.ForeignKey(CustomUser, on_delete=models.SET_DEFAULT, default=8)
    text = models.TextField(blank=False)
    status_open = models.BooleanField(default=True)
    announcement = models.BooleanField(default=False)


class Post(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    user_id = models.ForeignKey(CustomUser, on_delete=models.SET_DEFAULT, default=8)
    text = models.TextField(blank=False)
    upvote_count = models.IntegerField(default=0)

    def update_votes(self):
        votes = Vote.objects.filter(post=self)
        self.upvote_count = votes.aggregate(total=Sum('value'))['total'] or 0
        self.save()
        self.user_id.update_reputation_points()  # Update the user's reputation points

    def upvote(self, user):
        # Check for an existing vote
        existing_vote = Vote.objects.filter(user=user, post=self).first()
        
        if existing_vote and existing_vote.value == 1:
            # If the user has already upvoted, remove the upvote (neutralize)
            existing_vote.delete()
            print(f"User {user.id} neutralized upvote for post {self.id}")
        elif existing_vote and existing_vote.value == -1:
            # If the user has downvoted, change their vote to upvote
            existing_vote.value = 1
            existing_vote.save()
            print(f"User {user.id} changed downvote to upvote for post {self.id}")
        else:
            # If no existing vote, create a new upvote
            Vote.objects.create(user=user, post=self, value=1)
            print(f"User {user.id} upvoted post {self.id}")
        
        # Update votes and reputation points
        self.update_votes()

    def downvote(self, user):
        # Check for an existing vote
        existing_vote = Vote.objects.filter(user=user, post=self).first()
        
        if existing_vote and existing_vote.value == -1:
            # If the user has already downvoted, remove the downvote (neutralize)
            existing_vote.delete()
            print(f"User {user.id} neutralized downvote for post {self.id}")
        elif existing_vote and existing_vote.value == 1:
            # If the user has upvoted, change their vote to downvote
            existing_vote.value = -1
            existing_vote.save()
            print(f"User {user.id} changed upvote to downvote for post {self.id}")
        else:
            # If no existing vote, create a new downvote
            Vote.objects.create(user=user, post=self, value=-1)
            print(f"User {user.id} downvoted post {self.id}")
        
        # Update votes and reputation points
        self.update_votes()

class Vote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    value = models.IntegerField(choices=[(-1, 'Downvote'), (1, 'Upvote')])

    class Meta:
        unique_together = [('user', 'post')]

class Message(models.Model):
    sender = models.ForeignKey(CustomUser, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(CustomUser, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

class Report(models.Model):
    REASON_CHOICES = [
        ('harassment', 'Harassment or Hate Speech'),
        ('misinformation', 'Misinformation'),
        ('inappropriate', 'Inappropriate Content'),
        ('spam', 'Spam or Scam'),
        ('impersonation', 'Impersonation'),
        ('violence', 'Violence or Threats'),
        ('self_harm', 'Self-Harm or Suicide'),
    ]
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reports', default=1)
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='reports', default=1)
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    details = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report {self.id} - {self.reason}"