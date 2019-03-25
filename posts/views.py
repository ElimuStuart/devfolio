from django.shortcuts import render

from .models import Post

def index(request):
    recent_queryset = Post.objects.all().order_by('-timestamp')[:3]
    context = {
        'recent_queryset': recent_queryset,
    }
    return render(request, 'index.html', context)

def blog(request):
    return render(request, 'blog-single.html', {})