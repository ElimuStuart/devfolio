from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from tinymce import HTMLField
from taggit.managers import TaggableManager

class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(status='published')


class Post(models.Model):

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date='publish')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    thumbnail = models.ImageField()
    body = HTMLField()
    publish = models.DateTimeField(default=timezone.now)
    create = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')

    objects = models.Manager() # the default manage i.e Post.objects.all()
    published = PublishedManager() # our custom manager i.e Post.published.all()
    tags = TaggableManager()

    class Meta:
        ordering = ('-publish',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('posts:post_detail', args=[
            self.publish.year,
            self.publish.month,
            self.publish.day,
            self.slug
        ])

    # def get_update_url(self):
    #     return reverse('post_update', kwargs={
    #         'id': self.id
    #     })

    # def get_delete_url(self):
    #     return reverse('post_delete', kwargs={
    #         'id': self.id
    #     })

    # @property
    # def get_comments(self):
    #     return self.comments.all().order_by('-timestamp')

class Comment(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.SET_NULL)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return f"Comment by {self.name} on {self.post}"