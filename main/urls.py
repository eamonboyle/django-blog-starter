from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap

from main import views
from main.sitemaps import PostSitemap

from .feeds import LatestPostsFeed

sitemaps = {
	'posts': PostSitemap
}

urlpatterns = [
  	url(r'^admin/', admin.site.urls),
	url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
	url(r'^feed/$', LatestPostsFeed(), name='post_feed'),
	# post views
	url(r'^$', views.post_list, name='post_list'),
	url(r'^tag/(?P<tag_slug>[-\w]+)/$', views.post_list, name='post_list_by_tag'),
	# url(r'^$', views.PostListView.as_view(), name='post_list'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/'\
        r'(?P<post>[-\w]+)/$',
        views.post_detail, 
        name='post_detail'),
	url(r'^(?P<post_id>\d+)/share/$', views.post_share, name='post_share'),
]
