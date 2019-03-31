from django.db.models import Q
from django.core.paginator import PageNotAnInteger, Paginator, EmptyPage
from django.shortcuts import render

from .models import Post


def search(request):
    queryset = Post.objects.all()
    query = request.GET.get('q')
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) |
            Q(overview__icontains=query)
        ).distinct()
    context = {
        'queryset': queryset
    }

    return render(request, 'search_results.html', context)


def index(request):
    recent_queryset = Post.objects.all().order_by('-timestamp')[:3]
    context = {
        'recent_queryset': recent_queryset,
    }
    return render(request, 'index.html', context)

def blog(request):
    most_recent = Post.objects.order_by('-timestamp')[:5]
    post_list = Post.objects.all().order_by('-timestamp')
    paginator = Paginator(post_list, 4)
    page_request_var = 'page'
    page = request.GET.get(page_request_var)
    try:
        paginated_queryset = paginator.page(page)
    except PageNotAnInteger:
        paginated_queryset = paginator.page(1)
    except EmptyPage:
        paginated_queryset = paginator.page(paginator.num_pages)

    context = {
        'most_recent': most_recent,
        'queryset': paginated_queryset,
        'page_request_var': page_request_var,
        
    }
    return render(request, 'blog.html', context)

def post(request, id):
    return render(request, 'blog-single.html')

