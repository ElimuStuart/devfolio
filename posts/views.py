from django.db.models import Q
from django.core.paginator import PageNotAnInteger, Paginator, EmptyPage
from django.shortcuts import render, get_object_or_404, redirect, reverse

from .models import Post
# from .forms import CommentForm, PostForm

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

def post_list(request):
    object_list = Post.published.all()
    paginator = Paginator(object_list, 3)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # if page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # if page is out of range deliver the last page
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog.html', {'posts': posts, 'page':page})

def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post,
        slug=post,
        status='published',
        publish__year=year,
        publish__month=month,
        publish__day=day
    )
    return render(request, 'blog-single.html', {'post': post})

# def post_create(request):
#     title = 'Create'
#     author = get_author(request.user)
#     form = PostForm(request.POST or None, request.FILES or None)
#     if request.method == 'POST':
#         if form.is_valid():
#             form.instance.author = author
#             form.save()
#             return redirect(reverse('post_detail', kwargs={
#                 'id': form.instance.id
#             }))
#     context = {
#         'title': title,
#         'form': form,
#     }
#     return render(request, 'post_create.html', context)

# def post_update(request, id):
#     post = get_object_or_404(Post, id=id)
#     title = 'Create'
#     author = get_author(request.user)
#     form = PostForm(request.POST or None, request.FILES or None, instance=post)
#     if request.method == 'POST':
#         if form.is_valid():
#             form.instance.author = author
#             form.save()
#             return redirect(reverse('post_detail', kwargs={
#                 'id': form.instance.id,
#             }))
#     context = {
#         'title': title,
#         'form': form,
#     }
#     return render(request, 'post_create.html', context)

# def post_delete(request, id):
#     post = get_object_or_404(Post, id=id)
#     post.delete()
#     return redirect(reverse('post_list'))

