from django.shortcuts import render, get_object_or_404, Http404, redirect

from account.utility import human_readable_size
from blog.models import Blog
from cloud.models import Server, DataCenter
from config.settings import redis
from .models import Page, FAQ
from .utility import DatacenterPackage, remove_html_tags, get_date_persian


def error_404(reuqest, *args, **kwargs):
    return render(reuqest, 'main/404.html', status=404)


def error_500(reuqest, *args, **kwargs):
    return render(reuqest, 'main/500.html', status=500)


def home(request):
    home_page = get_object_or_404(Page, slug="home", is_active=True)
    blogs = Blog.objects.filter(is_active=True).order_by("-created")[:8]
    datacenters = DataCenter.objects.filter(is_active=True)
    datacenters_package = []
    for datacenter in datacenters:
        datacenter_package = DatacenterPackage(name=datacenter.name)
        datacenter_package.servers = Server.objects.filter(datacenter__name=datacenter.name, is_active=True).order_by("price")
        for server in datacenter_package.servers:
            for location in server.location.filter(is_active=True):
                if location.country.lower() not in [loc.country.lower() for loc in datacenter_package.locations] or location.city.lower() not in [loc.city.lower() for loc in datacenter_package.locations]:
                    datacenter_package.locations.append(location)
        datacenter_package.servers = datacenter_package.servers[:4]
        datacenters_package.append(datacenter_package)

    min_price = {}
    for datacenter_servers in [datacenter.servers for datacenter in datacenters_package]:
        for server in datacenter_servers:
            if server == datacenter_servers[0]:
                min_price[server.datacenter.name] = server.price
            server.ram = "Ram" + " : " + human_readable_size(server.ram)
            server.cpu = "CPU" + " : " + human_readable_size(server.cpu, cpu=True)
            server.disk = "Disk" + " : " + human_readable_size(server.disk)
            server.traffic = "Traffic" + " : " + human_readable_size(server.traffic)
            server.price_day = "روزانه" + " " + human_readable_size(server.price // 30, price=True)
            server.price = "ماهانه" + " " + human_readable_size(server.price, price=True)

    sorted_datacenters_package = []
    sorted_price = sorted(min_price.values())
    while len(sorted_price) != 0:
        for key, value in min_price.items():
            if value == sorted_price[0]:
                is_found = False
                for d in datacenters_package:
                    if d.name == key:
                        sorted_datacenters_package.append(d)
                        sorted_price.remove(sorted_price[0])
                        is_found = True
                        break
                if is_found:
                    break

    for blog in blogs:
        blog.content = remove_html_tags(blog.content)[:150]
        blog.updated = get_date_persian(blog.updated)

    faqs = FAQ.objects.filter(page=home_page, is_active=True)
    return render(request, 'main/home.html', {
        "page": home_page,
        "datacenters": sorted_datacenters_package,
        "blogs": blogs, "faqs": faqs
    })


def cloud_server(request):
    cloud_server_page = get_object_or_404(Page, slug="cloud-server", is_active=True)
    datacenters = DataCenter.objects.filter(is_active=True)
    datacenters_package = []
    for datacenter in datacenters:
        datacenter_package = DatacenterPackage(name=datacenter.name)
        datacenter_package.servers = Server.objects.filter(datacenter__name=datacenter.name, is_active=True).order_by("price")
        for server in datacenter_package.servers:
            for location in server.location.filter(is_active=True):
                if location.country.lower() not in [loc.country.lower() for loc in datacenter_package.locations] or location.city.lower() not in [loc.city.lower() for loc in datacenter_package.locations]:
                    datacenter_package.locations.append(location)
        datacenters_package.append(datacenter_package)

    min_price = {}
    for datacenter_servers in [datacenter.servers for datacenter in datacenters_package]:
        for server in datacenter_servers:
            if server == datacenter_servers[0]:
                min_price[server.datacenter.name] = server.price
            server.ram = "Ram" + " : " + human_readable_size(server.ram)
            server.cpu = "CPU" + " : " + human_readable_size(server.cpu, cpu=True)
            server.disk = "Disk" + " : " + human_readable_size(server.disk)
            server.traffic = "Traffic" + " : " + human_readable_size(server.traffic)
            server.price_day = "روزانه" + " " + human_readable_size(server.price // 30, price=True)
            server.price = "ماهانه" + " " + human_readable_size(server.price, price=True)

    sorted_datacenters_package = []
    sorted_price = sorted(min_price.values())
    while len(sorted_price) != 0:
        for key, value in min_price.items():
            if value == sorted_price[0]:
                is_found = False
                for d in datacenters_package:
                    if d.name == key:
                        sorted_datacenters_package.append(d)
                        sorted_price.remove(sorted_price[0])
                        is_found = True
                        break
                if is_found:
                    break

    faqs = cloud_server_page.faq.filter(is_active=True)
    return render(request, 'main/cloud-server.html', {
        "page": cloud_server_page,
        "datacenters": datacenters, "datacenters_package": sorted_datacenters_package,
        "faqs": faqs
    })


def page(request, slug):
    if slug in ["home", "cloud-server"]:
        raise Http404
    if request.user.is_staff:
        p = get_object_or_404(Page, slug=slug)
    else:
        p = get_object_or_404(Page, slug=slug, is_active=True)
    faqs = p.faq.filter(is_active=True)
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
