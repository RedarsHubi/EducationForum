from django import forms
from .models import CustomUser, Section, Category, Thread, Post, Message
from django_countries.fields import CountryField
from django.contrib.auth.forms import UserCreationForm

class CustomUserForm(forms.ModelForm):
    country = CountryField().formfield()
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=False)

    class Meta:
        model = CustomUser
        fields = ['bio', 'profile_picture', 'picture_url', 'signature', 'country', 'age', 'gender', 'display_gender', 'display_age']  # Add other fields as needed

    def clean_age(self):
        age = self.cleaned_data['age']
        if age < 12:
            raise forms.ValidationError("Age must be older.")
        if age > 120:
            raise forms.ValidationError("Are you a dinasaur? Enter the correct age.")
        
        return age

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email', 'name') 

class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['name']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'section']


class ThreadForm(forms.ModelForm):
    """ form in the admin page """
    class Meta:
        model = Thread
        fields = ['title', 'text', 'category']