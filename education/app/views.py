from django.shortcuts import render, redirect
from django.urls import reverse
from .models import CustomUser,  Section, Category, Post, Thread, Vote, Message, Report
from django.db.models import Count, Subquery, OuterRef, Q

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