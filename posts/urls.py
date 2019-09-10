from django.urls import path
from . import views
from .feeds import LatestPostFeed

app_name ='posts'

urlpatterns = [
    path('', views.index, name='index'),
    path('blog/', views.post_list,name='post_list'),
    path('tag/<slug:tag_slug>/', views.post_list,name='post_list_by_tag'),
    path('blog/<int:year>/<int:month>/<int:day>/<slug:post>/', views.post_detail, name='post_detail'),
    path('<int:post_id>/share/', views.post_share, name='post_share'),
    path('feed/', LatestPostFeed(), name='post_feed')
]