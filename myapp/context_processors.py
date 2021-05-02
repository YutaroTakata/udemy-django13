from .models import Category

def all_category(request):
  category_list = Category.objects.all()
  context = {
    'category_list': category_list,
  }
  return context