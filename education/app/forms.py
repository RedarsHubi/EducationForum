from django import forms
from .models import CustomUser, Section, Category, Thread, Post, Message
from django_countries.fields import CountryField
from django.contrib.auth.forms import UserCreationForm

class CustomUserForm(forms.ModelForm):
    """
    Form for updating CustomUser profile information.
    Includes fields for bio, profile picture, country, age, gender, and display preferences.
    """
    country = CountryField().formfield()
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=False)

    class Meta:
        model = CustomUser
        fields = ['bio', 'profile_picture', 'picture_url', 'signature', 'country', 'age', 'gender', 'display_gender', 'display_age']

    def clean_age(self):
        """
        Custom validation for the age field.
        Ensures the age is between 12 and 120 years.
        """
        age = self.cleaned_data['age']
        if age < 12:
            raise forms.ValidationError("Age must be older.")
        if age > 120:
            raise forms.ValidationError("Are you a dinosaur? Enter the correct age.")
        return age

class CustomUserCreationForm(UserCreationForm):
    """
    Form for creating a new CustomUser.
    Extends UserCreationForm to use CustomUser model and includes email and name fields.
    """
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email', 'name')

class RegisterForm(UserCreationForm):
    """
    Form for registering a new user.
    Extends UserCreationForm to include email field and uses CustomUser model.
    """
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ("name", "email", "password1", "password2")

    def save(self, commit=True):
        """
        Save the new user instance.
        Override to ensure email is saved.
        """
        user = super(RegisterForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
        
class SectionForm(forms.ModelForm):
    """
    Form for creating or updating a Section.
    """
    class Meta:
        model = Section
        fields = ['name']

class CategoryForm(forms.ModelForm):
    """
    Form for creating or updating a Category.
    """
    class Meta:
        model = Category
        fields = ['name', 'section']

class ThreadForm(forms.ModelForm):
    """
    Form for creating or updating a Thread in the admin page.
    """
    class Meta:
        model = Thread
        fields = ['title', 'text', 'category']

class PostForm(forms.ModelForm):
    """
    Form for creating or updating a Post in the admin page.
    """
    class Meta:
        model = Post
        fields = ['text']

class MessageForm(forms.ModelForm):
    """
    Form for creating or updating a Message.
    Includes a custom widget for the content field.
    """
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'cols': 50, 'placeholder': 'Type your message here...'}),
        }

