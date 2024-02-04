import random
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from config.settings import PAGINATION_BLOGS
from main.utility import remove_html_tags, get_date_persian
from .models import Blog, Category


def last_blogs():
    blog_list = Blog.objects.filter(is_active=True).order_by('-created')[:8]
    for blog in blog_list:
        blog.content = remove_html_tags(blog.content)[:150]
        blog.updated = get_date_persian(blog.updated)
    return blog_list

@ensure_csrf_cookie
def blog(request, slug):
    if request.user.is_staff:
        p = get_object_or_404(Blog, slug=slug)
    else:
        p = get_object_or_404(Blog, slug=slug, is_active=True)
    p.increase_view()
    p.created = get_date_persian(p.created)
    p.updated = get_date_persian(p.updated)
    first_category = p.category.first()
    blogs = list(Blog.objects.all().exclude(pk=p.pk).order_by("-created"))
    newest_blogs = blogs[:10]
    related_blogs = blogs
    count_related_blogs = 10
    if len(related_blogs) > count_related_blogs:
        related_blogs = []
        for i in range(count_related_blogs):
            chosen_blog = random.choice(blogs)
            related_blogs.append(chosen_blog)
            blogs.remove(chosen_blog)
    breadcrumbs = [p, first_category]
    if first_category.reply_id:
        x = Category.objects.get(pk=first_category.reply_id, is_active=True)
        breadcrumbs.append(x)
        while True:
            if not x.reply_id:
                break
            x = Category.objects.get(slug=x.reply_id, is_active=True)
            breadcrumbs.append(x)
    breadcrumbs = list(reversed(breadcrumbs))
    return render(request, 'blog/blog.html', {
        'blog': p, "category": first_category, "breadcrumbs": breadcrumbs, "related_blogs": related_blogs,
        "star": p.get_starts(), "newest_blogs": newest_blogs
    })


def category(request, slug):
    if slug == 'blog':
        raise Http404
    cat = get_object_or_404(Category, slug=slug, is_active=True)
    cat.increase_view()
    blogs = Blog.objects.filter(category__slug=slug, is_active=True).order_by("-created")
    paginator = Paginator(blogs, PAGINATION_BLOGS)
    page_number = request.GET.get("page", "1")
    try:
        blogs = paginator.page(page_number)
    except:
        raise Http404
    for blog in blogs:
        blog.content = remove_html_tags(blog.content)[:150]
        blog.created = get_date_persian(blog.created)
    breadcrumbs = [cat]
    if cat.reply_id:
        x = Category.objects.get(pk=cat.reply_id, is_active=True)
        breadcrumbs.append(x)
        while True:
            if not x.reply_id:
                break
            x = Category.objects.get(slug=x.reply_id, is_active=True)
            breadcrumbs.append(x)
    breadcrumbs = list(reversed(breadcrumbs))
    return render(request, "blog/blog-list.html", {"category": cat, "blogs": blogs, "breadcrumbs": breadcrumbs})


def list_of_blogs(request):
    cat = get_object_or_404(Category, slug='blog', is_active=True)
    cat.increase_view()
    blogs = Blog.objects.filter(is_active=True).order_by("-created")
    paginator = Paginator(blogs, PAGINATION_BLOGS)
    page_number = request.GET.get("page", '1')
    try:
        blogs = paginator.page(page_number)
    except Exception:
        raise Http404

    for blog in blogs:
        blog.content = remove_html_tags(blog.content)[:150]
        blog.created = get_date_persian(blog.created)
    breadcrumbs = [cat]
    return render(request, "blog/blog-list.html", {
        "blogs": blogs, 'category': cat, 'breadcrumbs': breadcrumbs
    })
