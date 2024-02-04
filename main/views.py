from django.shortcuts import render, get_object_or_404, Http404, redirect

from account.utility import human_readable_size
from blog.models import Blog
from cloud.models import Server, DataCenter
from config.settings import redis
from .models import Page, FAQ
from .utility import remove_html_tags, get_date_persian
from blog.views import last_blogs


def error_404(reuqest, *args, **kwargs):
    return render(reuqest, 'main/404.html', status=404)


def error_500(reuqest, *args, **kwargs):
    return render(reuqest, 'main/500.html', status=500)


def home(request):
    home_page = get_object_or_404(Page, slug="home", is_active=True)

    faqs = FAQ.objects.filter(page=home_page, is_active=True)
    return render(request, 'main/home.html', {
        "page": home_page,
        "blogs": last_blogs(), "faqs": faqs
    })


def page(request, slug):
    if slug in ["home", "cloud-server"]:
        raise Http404
    if request.user.is_staff:
        p = get_object_or_404(Page, slug=slug)
    else:
        p = get_object_or_404(Page, slug=slug, is_active=True)
    faqs = FAQ.objects.filter(page=p, is_active=True)
    return render(request, 'main/page.html', {'page': p, "faqs": faqs})


def link_shortener(request, counter):
    url = None
    for key, value in redis.hgetall("ShortLinks").items():
        if str(counter) == value:
            url = key
            break
    if not url:
        raise Http404
    return redirect(url)
