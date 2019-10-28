from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.core.mail import send_mail
from django.db.models import Count

from taggit.models import Tag

from .models import Post, Comment
from .forms import EmailPostForm, CommentForm


# Create your views here.
def post_list(request, tag_slug=None):
	object_list = Post.objects.all()
	tag = None

	if tag_slug:
		tag = get_object_or_404(Tag, slug=tag_slug)
		object_list = object_list.filter(tags__in=[tag])

	paginator = Paginator(object_list, 3)
	page = request.GET.get('page')
	try:
		posts = paginator.page(page)
	except PageNotAnInteger:
		posts = paginator.page(1)
	except EmptyPage:
		posts = paginator.page(paginator.num_pages)
	
	return render(request, 'main/post/list.html', {
		'page': page,
		'posts': posts,
		'tag': tag
	})

class PostListView(ListView):
	queryset = Post.published.all()
	context_object_name = 'posts'
	paginate_by = 3
	template_name = 'main/post/list.html'

def post_detail(request, year, month, day, post):
	post = get_object_or_404(Post, slug=post,
							status='published',
							publish__year=year,
							publish__month=month,
							publish__day=day)

	# list of active comments
	comments = post.comments.filter(active=True)

	if request.method == 'POST':
		# a comment was posted
		comment_form = CommentForm(data = request.POST)
		if comment_form.is_valid():
			# create comment object
			new_comment = comment_form.save(commit=False)
			# assign the current post to the comment
			new_comment.post = post
			# save to database
			new_comment.save()
	else:
		comment_form = CommentForm()
		new_comment = False

	# List of similar posts
	post_tags_ids = post.tags.values_list('id', flat=True)
	similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
	similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]

	return render(request, 'main/post/detail.html', {
		'post': post,
		'comments': comments,
		'comment_form': comment_form,
		'new_comment': new_comment,
		'similar_posts': similar_posts
	})

def post_share(request, post_id):
	# retrieve the post by id
	post = get_object_or_404(Post, id=post_id, status='published')
	sent = False

	if request.method == 'POST':
		# form was submitted
		form = EmailPostForm(request.POST)
		if form.is_valid():
			# form fields passed validation
			cd = form.cleaned_data
			# post_url = request.build_absolute_uri(post.get_absolute_url())
            # subject = '{} ({}) recommends you reading "{}"'.format(cd['name'], cd['email'], post.title)
            # message = 'Read "{}" at {}\n\n{}\'s comments: {}'.format(post.title, post_url, cd['name'], cd['comments'])
            # send_mail(subject, message, 'admin@myblog.com', [cd['to']])
			sent = True
	else:
		form = EmailPostForm()
	
	return render(request, 'main/post/share.html', {'post': post, 'form': form, 'sent': sent})