"""
URL configuration for education project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from app.models import CustomUser
from app import views
from django.conf import settings
from django.conf.urls.static import static
from channels.routing import ProtocolTypeRouter, URLRouter
from .consumers import InboxConsumer, ChatConsumer


websocket_urlpatterns = [
    path('ws/inbox/', InboxConsumer.as_asgi()),
    path('ws/chat/', ChatConsumer.as_asgi()),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.landing_page, name='landing_page'),
    path('home/', views.home, name='home'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/profile/', views.profile, name='profile'),
    path('accounts/register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('login/', views.custom_login, name='login'),
    path('threads/', views.threads, name='threads'),
    path('thread_page/', views.thread_page, name='thread_page'),
    path('user/', views.user, name='user'),
    path('upvote/<int:post_id>/', views.upvote_post, name='upvote_post'),
    path('downvote/<int:post_id>/', views.downvote_post, name='downvote_post'),
    path('vote_color/<int:post_id>/', views.vote_color, name='vote_color'),
    path('thread_creation/', views.thread_creation, name='thread_creation'),
    path('post_creation/', views.post_creation, name='post_creation'),
    path('delete_post/<int:post_id>/', views.delete_post, name='delete_post'),
    path('delete_thread/<int:thread_id>/', views.delete_thread, name='delete_thread'),
    path('edit_post/<int:post_id>/', views.edit_post, name='edit_post'),
    path('save_post/<int:post_id>/', views.save_post, name='save_post'),
    path('save_thread/<int:thread_id>/', views.save_thread, name='save_thread'),
    path('thread_page/<int:thread>/', views.thread_page, name='thread_page'),
    path('thread_page/<int:post_id>/', views.thread_page, name='thread_page'),
    path('search/results/', views.search_results, name='search_results'),
    path('search/suggestions/', views.search_suggestions, name='search_suggestions'),
    path('inbox/', views.inbox, name='inbox'),path('report_post/<int:post_id>/', views.report_post, name='report_post'),
    path('reported_posts/', views.reported_posts, name='reported_posts'),
    path('handle_report/<int:report_id>/', views.handle_report, name='handle_report'),
    path('thread_page/<int:post_id>/', views.thread_page, name='thread_page'),
    path('report_thread/<int:thread_id>/', views.report_thread, name='report_thread'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)