from django.db.models import Q, Count
from django.core.paginator import PageNotAnInteger, Paginator, EmptyPage
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.views.generic import ListView
from django.core.mail import send_mail
from taggit.models import Tag

from .models import Post, Comment
from .forms import EmailPostForm, CommentForm

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
    recent_queryset = Post.published.order_by('-publish')[:5]
    context = {
        'recent_queryset': recent_queryset,
    }
    return render(request, 'index.html', context)

def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    latest_posts = Post.published.order_by('-publish')[:5]
    display_title = "Latest"
    tags = Tag.objects.all()[:5]


    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

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
    return render(request, 'blog.html', {'posts': posts, 'page':page, 'tag':tag, 'tags':tags, 'latest_posts':latest_posts, 'display_title': display_title})

class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog.html'

def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post,
        slug=post,
        status='published',
        publish__year=year,
        publish__month=month,
        publish__day=day
    )

    # list of active comments for this post
    comments = post.comments.filter(active=True)

    new_comment = None

    if request.method == 'POST':
        # comment was posted
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # create comment obj, don;t save to db yet
            new_comment = comment_form.save(commit=False)
            # attach current post to the comment
            new_comment.post = post
            # save comment to db
            new_comment.save()
    else:
        comment_form = CommentForm()

    # list similar posts
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]
    display_title = 'Similar'

    return render(request, 'blog-single.html', {
        'post': post, 
        'comments': comments, 
        'new_comment': new_comment,
        'comment_form': comment_form,
        'similar_posts': similar_posts,
        'display_title': display_title
    })

def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == 'POST':
        # form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # form fields passed validation
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} ({cd['email']}) recommends you reading {post.title}"
            message = f"""Read "{post.title}" at {post_url}\n\n {cd['name']}'s comments: {cd['comments']} """
            send_mail(subject, message, 'stue@devfolio.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'share.html', {'post': post, 'form': form, 'sent':sent})

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

