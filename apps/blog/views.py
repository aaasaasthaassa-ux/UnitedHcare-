from django.views.generic import ListView, DetailView
from django.utils import timezone
from .models import Post


class PostListView(ListView):
    model = Post
    template_name = 'blog/list.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_queryset(self):
        return Post.objects.filter(status='published', published_at__lte=timezone.now()).order_by('-published_at')


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        return Post.objects.filter(status='published', published_at__lte=timezone.now())
