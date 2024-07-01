from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout, authenticate, login, get_user_model
from django.contrib import messages
from .models import CustomUser, Section, Category, Post, Thread, Vote, Message, Report
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm, CustomUserForm, ThreadForm, PostForm, MessageForm, RegisterForm
from django.db.models import Count, Subquery, OuterRef, Q
from django.urls import reverse
import json
from datetime import date, timedelta
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from collections import OrderedDict
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction


def landing_page(request):
    if request.user.is_authenticated:
        return redirect(reverse('home'))
    return render(request, 'landing_page.html')

def home(request):
    # Logic to fetch data from the database or perform other operations
    sections = Section.objects.all()  
    categories = Category.objects.all()
    categories = categories.annotate(
        thread_count=Subquery(
            Thread.objects.filter(category_id=OuterRef('id')).values('category_id').annotate(count=Count('id')).values('count')[:1]
        ),
        post_count=Subquery(
            Post.objects.filter(thread_id__category_id=OuterRef('id')).values('thread_id__category_id').annotate(count=Count('id')).values('count')[:1]
        ),
        last_thread=Subquery(
            Thread.objects.filter(category_id=OuterRef('id')).order_by('-created_at').values('created_at')[:1]
        ),
        last_thread_user_id=Subquery(
            Thread.objects.filter(category_id=OuterRef('id'))
                        .order_by('-created_at')
                        .values('user_id')[:1]
        ),
        last_thread_user_name=Subquery(
            CustomUser.objects.filter(id=OuterRef('last_thread_user_id'))
                        .values('name')[:1]
        ),
        last_thread_id=Subquery(
            Thread.objects.filter(category_id=OuterRef('id')).order_by('-created_at').values('id')[:1]
        ),
        last_thread_name=Subquery(
            Thread.objects.filter(category_id=OuterRef('id')).order_by('-created_at').values('title')[:1]
        )
    )
    user = request.user
    if request.user.is_authenticated:
        unread_counts = Message.objects.filter(receiver=request.user, is_read=False).count()
    else:
        unread_counts = 0
    print("User in home view:", user)
    
    return render(request, 'home.html', {'user': user, 'sections': sections, 'categories': categories, 'unread_counts': unread_counts})  

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            print("User registered successfully")  # Add this print statement
            return redirect('login')  # Redirect to the login page after successful registration
        else:
            print("Form errors:", form.errors)  # Add this print statement to check form errors
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

@login_required
def profile(request):
    user = request.user
    error_msg = None
    print("User in profile view:", user)
    if request.method == 'POST':
        form = CustomUserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            profile_picture = form.cleaned_data.get('profile_picture')
            picture_url = form.cleaned_data.get('picture_url')
            if profile_picture and picture_url:
                error_msg = "You can only provide either a profile picture or a picture URL, not both."
            else:
                form.save()
                return redirect('profile')  # Redirect to the profile page after successful update
        else:
            error_msg = "There was an error. Please correct the form."
            # Add error message to display in the template
            messages.error(request, error_msg) # Redirect to the profile page after successful update
    else:
        form = CustomUserForm(instance=user)
    return render(request, 'profile.html', {'form': form, 'user': user, 'messages': error_msg })


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to the home page after successful login
            else:
                # Authentication failed, handle accordingly
                messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def threads(request):
    # Logic to fetch data from the database or perform other operations
    category = request.GET.get('category')
    category_name, section_id = Category.objects.filter(id=category).values_list('name', 'section_id').first()
    section_name = Section.objects.filter(id=section_id).values('name').first()

    threads = Thread.objects.filter(category_id=category)
    categories = Category.objects.all()
    for thread in threads:
        post_count = Post.objects.filter(thread_id=thread.id).count() + 1
        last_post_data = Post.objects.filter(thread_id=thread.id).order_by('-created_at').values_list('created_at', 'user_id').first()
        
        thread.post_count = post_count
        thread.last_post_date, thread.last_post_user_id = last_post_data if last_post_data else (None, None)
        
        if thread.last_post_user_id:
            last_post_user_name = CustomUser.objects.filter(id=thread.last_post_user_id).values_list('name', flat=True).first()
            thread.last_post_user_name = last_post_user_name

    return render(request, 'threads.html', {'threads': threads, 'categories': categories, 'category_name': category_name, 'section_name': section_name['name'], }) 

def thread_page(request):
    # Logic to fetch data from the database or perform other operations
    thread_id = request.GET.get('thread')
    threads = get_object_or_404(Thread, pk=thread_id)

    category_name, section_id = Category.objects.filter(id=threads.category_id).values_list('name', 'section_id').first()
    section_name = Section.objects.filter(id=section_id).values('name').first()

    threads.views += 1
    threads.save()
    posts = Post.objects.filter(thread_id=thread_id).select_related('user_id').order_by('created_at')
    post_count = Post.objects.filter(thread_id=thread_id).count() + 1
    author = threads.user_id
    current_user = request.user

    form = PostForm()

    return render(request, 'thread_page.html', {
        'posts': posts, 'threads': threads, 'category_name': category_name, 'section_name': section_name['name'], 
        'post_count': post_count, 'author': author, 'current_user': current_user, 'form': form,
        'messages': messages.get_messages(request), 
        })

def user(request):
    # Logic to fetch data from the database or perform other operations
    user_id = request.GET.get('id')
    
    # Query the CustomUser model to find a user with the given ID
    user = CustomUser.objects.filter(id=user_id).first()
    current_user = request.user

    if current_user == user:
        return redirect('profile')
    else:
        return render(request, 'user.html', {'user': user, 'current_user': current_user}) 

@login_required
def thread_creation(request):
    if request.method == 'POST':
        form = ThreadForm(request.POST)
        if form.is_valid():
            thread_instance = form.save(commit=False)
            thread_instance.user_id = request.user # Set the user_id of the thread to the current user
            thread_instance.save()

            thread_id = thread_instance.id
            messages.success(request, "Thread created successfully")
            return redirect(reverse('thread_page') + '?thread=' + str(thread_id))
        else:
            print("Form errors:", form.errors)
    else:
        form = ThreadForm()
    categories = Category.objects.all()
    return render(request, 'thread_creation.html', {'form': form, 'categories': categories})

@login_required
def post_creation(request):
    thread_id = request.GET.get('thread')
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post_instance = form.save(commit=False)
            post_instance.thread_id = thread_id
            post_instance.user_id = request.user # Set the user_id of the thread to the current user
            post_instance.save()
            thread_title = Thread.objects.filter(id=thread_id).values('title')
            return render(request, 'partial_post.html', {'post': post_instance, 'title': thread_title, 'current_user': request.user})
        else:
            print("Form errors:", form.errors)
    
@login_required
def upvote_post(request, post_id):
    user = request.user
    post = Post.objects.filter(id=post_id).first()
    post.upvote(user)


    response_data = {
        'upvote_count': post.upvote_count
    }
    return JsonResponse(response_data)

@login_required
def downvote_post(request, post_id):
    user = request.user
    post = Post.objects.filter(id=post_id).first()
    post.downvote(user)
    


    response_data = {
        'upvote_count': post.upvote_count
    }
    return JsonResponse(response_data)

def vote_color(request, post_id):
    user = request.user
    existing_vote = Vote.objects.filter(user=user, post=post_id).first()
    if existing_vote and existing_vote.value == 1:
        vote = 1
    elif existing_vote and existing_vote.value == -1:
        vote = -1
    else:
        vote = 0
    response_data = {
         'vote': vote
    }
    return JsonResponse(response_data)
    
    
@login_required
def delete_post(request, post_id):
    if request.method == 'DELETE':
        # Get the post object, or return a 404 Not Found if it doesn't exist
        post = get_object_or_404(Post, pk=post_id)
        
        # Check if the current user is the author of the post
        if post.user_id != request.user:
            # Return a 403 Forbidden if the user is not the author of the post
            return HttpResponse(status=403)
        
        # Delete the post from the database
        post.delete()
        
        # Return a 204 No Content response on successful deletion
        return HttpResponse(status=204)
    
    # If the request method is not DELETE, return a 405 Method Not Allowed
    return HttpResponse(status=405)

@login_required
def delete_thread(request, thread_id):
    # Get the post object, or return a 404 Not Found if it doesn't exist
    thread = get_object_or_404(Thread, pk=thread_id)
        
    # Check if the current user is the author of the post
    if thread.user_id != request.user:
        # Return a 403 Forbidden if the user is not the author of the post
        return HttpResponse(status=403)
        
        # Delete the post from the database
    thread.delete()

    return redirect('home')


@login_required
@require_POST
def edit_post(request, post_id):
    # Get the post to edit
    post = get_object_or_404(Post, id=post_id, user=request.user)

    # Parse the incoming data (JSON or form data)
    try:
        # In this example, we're assuming JSON data is sent in the request body
        data = request.body.decode('utf-8')
        request_data = json.loads(data)
        new_text = request_data.get('text')

        if new_text:
            # Update the post text
            post.text = new_text
            post.save()

            # Return success response
            return JsonResponse({'success': True})
        else:
            # Invalid data in request
            return JsonResponse({'success': False, 'error': 'No text provided'}, status=400)
    
    except Exception as e:
        # Handle any unexpected errors
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@require_POST
@login_required
def save_post(request, post_id):
    if request.method == 'POST':
        # Get the post instance
        post = get_object_or_404(Post, id=post_id, user_id=request.user)        
        # Get the new text from the request body
        data = json.loads(request.body)
        new_text = data.get('text')
        
        # Update the post's text
        post.text = new_text
        post.save()
        
        # Return a JSON response indicating success
        return JsonResponse({'success': True})
    
    # If the request method is not POST, return an error
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

@login_required
@require_POST
def save_thread(request, thread_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    try:
        thread = Thread.objects.get(pk=thread_id, user_id=request.user)
    except Thread.DoesNotExist:
        return JsonResponse({'error': 'Post not found or permission denied'}, status=404)

    # Get the new text from the request
    data = request.body.decode('utf-8')
    json_data = json.loads(data)
    new_text = json_data.get('text')

    # Update the post text
    thread.text = new_text
    thread.save()

    return JsonResponse({'success': True})
    
