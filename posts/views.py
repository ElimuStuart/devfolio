from django.db.models import Q
from django.core.paginator import PageNotAnInteger, Paginator, EmptyPage
from django.shortcuts import render, get_object_or_404, redirect, reverse

from .models import Post, Comment, Author
from .forms import CommentForm, PostForm

import bs4
import urllib.request, re

WPM = 200
WORD_LENGTH = 5

def get_author(user):
    qs = Author.objects.filter(user=user)
    if qs.exists:
        return qs[0]
    return None

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



# extracting visible webpage text
def extract_text(url):
    html = urllib.request.urlopen(url).read()
    soup = bs4.BeautifulSoup(html, 'html.parser')
    texts = soup.findAll(text=True)
    return texts

# filter unnecessary page content
def is_visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif isinstance(element, bs4.element.Comment):
        return False
    elif element.string == '\n':
        return False
    return True

def filter_visible_text(page_texts):
    return filter(is_visible, page_texts)

# estimate reading time
def count_words_in_text(text_list, word_length):
    total_words = 0
    for current_text in text_list:
        total_words += len(current_text)/word_length
    return total_words

def estimate_reading_time(url):
    texts = extract_text(url)
    filtered_text = filter_visible_text(texts)
    total_words = count_words_in_text(filtered_text, WORD_LENGTH)
    return round(total_words/WPM)

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
    post = get_object_or_404(Post, id=id)
    comments = post.comments.filter(parent__isnull=True).order_by('-timestamp')
    post_list = Post.objects.all().order_by('-timestamp')
    most_recent = Post.objects.order_by('-timestamp')[:5]

    # TODO: get article reading time
    read_time = estimate_reading_time(url)

    form = CommentForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.instance.user = request.user
            parent_obj = None
            try:
                parent_id = int(request.POST.get('parent_id'))
            except:
                parent_id = None
            if parent_id:
                parent_obj = Comment.objects.get(id=parent_id)
                if parent_obj:
                    comment_reply = form.save(commit=False)
                    comment_reply.parent = parent_obj
            form.instance.post = post
            form.save()
            return redirect(reverse('post_detail', kwargs={
                'id': post.id,
            }))
    context = {
        'form':form,
        'post': post,
        'most_recent': most_recent,
        'queryset': post_list,
        'comments': comments,
    }
    return render(request, 'blog-single.html', context)

def post_create(request):
    title = 'Create'
    author = get_author(request.user)
    form = PostForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            form.instance.author = author
            form.save()
            return redirect(reverse('post_detail', kwargs={
                'id': form.instance.id
            }))
    context = {
        'title': title,
        'form': form,
    }
    return render(request, 'post_create.html', context)

def post_update(request, id):
    post = get_object_or_404(Post, id=id)
    title = 'Create'
    author = get_author(request.user)
    form = PostForm(request.POST or None, request.FILES or None, instance=post)
    if request.method == 'POST':
        if form.is_valid():
            form.instance.author = author
            form.save()
            return redirect(reverse('post_detail', kwargs={
                'id': form.instance.id,
            }))
    context = {
        'title': title,
        'form': form,
    }
    return render(request, 'post_create.html', context)

def post_delete(request, id):
    post = get_object_or_404(Post, id=id)
    post.delete()
    return redirect(reverse('post_list'))

