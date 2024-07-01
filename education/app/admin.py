from django.contrib import admin
from .models import Section, Category, Thread, Post, CustomUser

admin.site.register(Section)
admin.site.register(Category)
admin.site.register(Thread)
admin.site.register(Post)
admin.site.register(CustomUser)
