import jdatetime
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from account.utility import human_readable_size
from config.settings import PAGINATION_SERVERS, API_URL
from .forms import CreateServerCloudFrom
from .models import Server, ServerRent, ActivityServer, Location, Category


@login_required()
def home(request):
    return redirect(reverse("server-list", urlconf="cloud.urls"))


@login_required()
def server_list(request):
    servers = ServerRent.objects.filter(user=request.user, is_active=True).order_by("-created")
    paginator = Paginator(servers, PAGINATION_SERVERS)
    page_number = request.GET.get("page", "1")
    try:
        page_obj = paginator.page(page_number)
    except Exception:
        return Http404()
    for server in page_obj:
        server.created = jdatetime.datetime.fromgregorian(datetime=server.created).strftime('%H:%M:%S | %Y/%m/%d')
    return render(request, "cloud/server-list.html", {"servers": page_obj})


@login_required()
def server_create(request):
    servers = Server.objects.filter(is_active=True).order_by("price")
    locations = Location.objects.filter(is_active=True)
    for server in servers:
        server.price_day = int(server.price / 30)
        server.price_day = human_readable_size(server.price_day, price=True)
        server.ram = human_readable_size(server.ram)
        server.cpu = human_readable_size(server.cpu, cpu=True)
        server.disk = human_readable_size(server.disk)
        server.traffic = human_readable_size(server.traffic)
        server.price = human_readable_size(server.price, price=True)
    page = request.GET.get('page', '1')
    url_api_server_list = API_URL[:-1] + reverse('server-list', 'api.urls') + f'?page={page}'
    return render(
        request, 
        "cloud/server-create.html", 
        {
            "servers": servers, 
            'locations': locations,
            'url_api_server_list': url_api_server_list,
            'form': CreateServerCloudFrom
        }
    )


@login_required()
def server_detail(request, slug):
    server = get_object_or_404(ServerRent, user=request.user, slug=slug, is_active=True)
    activities = ActivityServer.objects.filter(server=server).order_by('-created')[:3]
    server.server.ram = human_readable_size(server.server.ram)
    server.server.cpu = human_readable_size(server.server.cpu, cpu=True)
    server.server.disk = human_readable_size(server.server.disk)
    server.server.traffic = human_readable_size(server.server.traffic)
    server.server.price = human_readable_size(server.server.price, price=True)
    server.cost = human_readable_size(server.cost, price=True)
    for activity in activities:
        for a in ActivityServer.ACTIVITY_CHOICES:
            if a[0] == activity.activity:
                activity.activity = a[1]
        activity.created = jdatetime.datetime.fromgregorian(datetime=activity.created).strftime('%H:%M:%S | %Y/%m/%d')
    return render(request, "cloud/server-detail.html", {"server": server, 'activities': activities})


@login_required()
def server_activity(request, slug):
    server = get_object_or_404(ServerRent, user=request.user, slug=slug, is_active=True)
    activities = ActivityServer.objects.filter(server=server).order_by('-created')
    page = request.GET.get('page', '1')
    pages = Paginator(activities, 25)
    try:
        activities = pages.page(page)
    except:
        raise Http404
    for activity in activities:
        for a in ActivityServer.ACTIVITY_CHOICES:
            if a[0] == activity.activity:
                activity.activity = a[1]
        activity.created = jdatetime.datetime.fromgregorian(datetime=activity.created).strftime('%H:%M:%S | %Y/%m/%d')

    return render(request, "cloud/server-activity.html", {"server": server, 'activities': activities})


@login_required()
def server_info(request, slug):
    server = get_object_or_404(ServerRent, user=request.user, slug=slug, is_active=True)
    return render(request, "cloud/server-info.html", {"server": server})



def category(request, slug):
    cat = get_object_or_404(Category, slug=slug)
    server_list = Server.objects.filter(category=cat, is_active=True).order_by('price')
    page = request.GET.get('page', '1')
    pages = Paginator(server_list, 25)
    try:
        server_list = pages.page(page)
    except:
        raise Http404
    for server in server_list:
        server.price_day = int(server.price / 30)
        server.price_day = human_readable_size(server.price_day, price=True)
        server.ram = human_readable_size(server.ram)
        server.cpu = human_readable_size(server.cpu, cpu=True)
        server.disk = human_readable_size(server.disk)
        server.traffic = human_readable_size(server.traffic)
        server.price = human_readable_size(server.price, price=True)
    return render(request, 'cloud/server-cloud-list.html', {'server_list': server_list, 'page': cat})

def category_main(request):
    cat = get_object_or_404(Category, slug='home')
    server_list = Server.objects.filter(category=cat, is_active=True).order_by('price')
    page = request.GET.get('page', '1')
    pages = Paginator(server_list, 25)
    try:
        server_list = pages.page(page)
    except:
        raise Http404
    for server in server_list:
        server.price_day = int(server.price / 30)
        server.price_day = human_readable_size(server.price_day, price=True)
        server.ram = human_readable_size(server.ram)
        server.cpu = human_readable_size(server.cpu, cpu=True)
        server.disk = human_readable_size(server.disk)
        server.traffic = human_readable_size(server.traffic)
        server.price = human_readable_size(server.price, price=True)
    return render(request, 'cloud/server-cloud.html', {'server_list': server_list, 'page': cat})