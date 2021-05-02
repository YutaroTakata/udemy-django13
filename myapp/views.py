from django.shortcuts import render, resolve_url, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import (
  TemplateView, ListView, CreateView, 
  DetailView, UpdateView, DeleteView
)
from .models import Post, Like, Category
from .forms import PostForm, LoginForm, SignUpForm, SearchForm
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator

class OnlyMyPostMixin(UserPassesTestMixin):
  raise_exception = False
  def test_func(self):
    post = Post.objects.get(id=self.kwargs['pk'])
    return post.author == self.request.user

class Index(ListView):
  model = Post
  template_name = 'myapp/index.html'

class PostCreate(LoginRequiredMixin, CreateView):
  model = Post
  form_class = PostForm
  success_url = reverse_lazy('myapp:index')

  def form_valid(self, form):
    form.instance.author_id = self.request.user.id
    return super(PostCreate, self).form_valid(form)

  def get_success_url(self):
    messages.success(self.request, 'Postを登録しました。')
    return resolve_url('myapp:index')

class PostDetail(DetailView):
  model = Post

class PostUpdate(OnlyMyPostMixin, UpdateView):
  model = Post
  form_class = PostForm

  def get_success_url(self):
    messages.info(self.request, 'Postを更新しました。')
    return resolve_url('myapp:post_detail', pk=self.kwargs['pk'])
  # success_url = reverse_lazy('myapp:index')

class PostDelete(OnlyMyPostMixin, DeleteView):
  model = Post

  def get_success_url(self):
    messages.info(self.request, 'Postを削除しました。')
    return resolve_url('myapp:index')

class PostList(ListView):
  model = Post
  paginate_by = 2

  def get_queryset(self):
    return Post.objects.all().order_by('-created_at')

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    category = Category.objects.all()
    context['category'] = category
    return context
    

class Login(LoginView):
  form_class = LoginForm
  template_name = 'myapp/login.html'

class Logout(LogoutView):
  template_name = 'myapp/logout.html'

class SignUp(CreateView):
  form_class = SignUpForm
  template_name = 'myapp/signup.html'
  success_url = reverse_lazy('myapp:index')

  def form_valid(self, form):
    user = form.save()
    login(self.request, user)
    self.object = user
    messages.info(self.request, 'ユーザー登録をしました')
    return HttpResponseRedirect(self.get_success_url())

@login_required
def Like_add(request, post_id):
  post = Post.objects.get(id=post_id)
  is_liked = Like.objects.filter(user=request.user, post=post_id).count()
  if is_liked:
    messages.info(request, 'すでにお気に入りに追加済みです。')
    return redirect('myapp:post_detail', post_id)
  else:
    like = Like(
      user = request.user,
      post = post
    )
    like.save()
    messages.success(request, 'お気に入りに追加しました。')
    return redirect('myapp:post_detail', post_id)

def Search(request):
  if request.method == 'POST':
    searchform = SearchForm(request.POST)

    if searchform.is_valid():
      freeword = searchform.cleaned_data['freeword']
      search_list = Post.objects.filter(Q(title__icontains=freeword) | Q(content__icontains=freeword))

    params = {
      'search_list': search_list,
    }
    return render(request, 'myapp/search.html', params)