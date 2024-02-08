import datetime
import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from rest_framework.decorators import action
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView, Response
from rest_framework.viewsets import ViewSet

from account.models import User
from account.utility import is_phone_correct, get_user_agent, send_code, login_register_user, check_amount
from blog.models import Blog
from cloud.forms import CreateServerCloudFrom
from cloud.models import Server as ServerCloud, ServerRent, ActivityServer
from config.settings import redis, PANEL_URL
from wallet.gateway import ZarinPalRequest
from wallet.models import Wallet, ServerCost
from wallet.models import ZarinPal
from .permissions import IsOwnerServer
from .serialize import ServerCloudSerializer
from .utility import get_datacenter, is_server_limited, set_server_limit


def submit_blog_review(request, slug):
    if request.method != "POST":
        return HttpResponse(status=410)
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    answer = body["answer"]
    if answer not in [True, False] or not get_user_agent(request):
        raise Http404
    data = {"response": False, "message": "فقط کاربران عضو شده می توانند رأی ثبت کنند"}
    if not request.user.is_authenticated:
        return JsonResponse(data)
    blog = get_object_or_404(Blog, slug=slug, is_active=True)
    blog.submit_vote(user=request.user, blog=blog, answer=answer)
    data["response"] = True
    data["message"] = "رأی شما با موفقیت ثبت شد"
    return JsonResponse(data)


def check_phone(request):
    if request.method != "POST":
        return HttpResponse(status=410)
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    phone = body["phone"]
    hash_id = body["hash_id"]
    data = {"response": False, "message": "شماره تلفن اشتباه است"}
    phone = is_phone_correct(phone)
    if not phone or not get_user_agent(request):
        return JsonResponse(data)
    generated_code, hash_id = send_code(request, phone, hash_id)
    if generated_code:
        data["response"] = True
        data["hash_id"] = hash_id
        data["message"] = "کد تایید برای شماره {} ارسال شد".format(phone)
    else:
        data["message"] = "خطا در ارسال کد"
    return JsonResponse(data)


def check_code(request):
    if request.method != "POST":
        return HttpResponse(status=410)
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    phone = body["phone"]
    code = body["code"]
    hash_id = body["hash_id"]
    data = {"response": False, "message": "خطا در بررسی اطلاعات"}
    phone = is_phone_correct(phone)
    user_agent = get_user_agent(request)
    if not phone or not user_agent:
        return JsonResponse(data)
    real_code = redis.get(f"VerificationHashId-{hash_id}")
    if real_code is None:
        data["message"] = "کد منقضی شده است"
        return JsonResponse(data)
    if real_code != code:
        data["message"] = "کد اشتباه است"
        return JsonResponse(data)
    login_register_user(request, phone, user_agent, hash_id)
    data["response"] = True
    data["message"] = "با موفقیت وارد شدید"
    data["next"] = PANEL_URL
    return JsonResponse(data)


@login_required()
def payment(request):
    if request.method != "POST":
        return HttpResponse(status=410)
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    amount = body["amount"]
    data = {"response": False, "message": "مبلغ وارد شده کمتر از حد مجاز می باشد"}
    if not check_amount(amount) or not get_user_agent(request):
        return JsonResponse(data)
    try:
        user = User.objects.get(pk=request.user.pk)
    except Exception:
        data["message"] = "عملیات ناموفق بود"
        return JsonResponse(data)
    amount = int(amount)
    description = "افزایش اعتبار"
    zarin_pal = ZarinPal.objects.create(user=user, amount=amount, description=description)
    pal = ZarinPalRequest()
    gate = pal.create_gateway(
        amount=amount,
        description=description,
        callback_url=f"{PANEL_URL}callback/zarinpal/{zarin_pal.pk}/"
    )
    zarin_pal.status_code = gate.code
    zarin_pal.authority = gate.authority
    zarin_pal.save()
    if gate.code != 100:
        data["message"] = "انتقال به درگاه پرداخت ناموفق بود"
        return JsonResponse(data)
    data["response"] = True
    data["message"] = "انتقال به درگاه پرداخت موفق بود"
    data["next"] = gate.url
    return JsonResponse(data)


class ServerCloudDetail(LoginRequiredMixin, RetrieveAPIView):
    serializer_class = ServerCloudSerializer
    lookup_field = 'slug'
    
    def get_queryset(self):
        slug = self.kwargs.get('slug', None)
        if not slug:
            raise Http404
        return ServerCloud.objects.filter(slug=slug, is_active=True)


class ServerCloudList(LoginRequiredMixin, ListAPIView):
    serializer_class = ServerCloudSerializer

    def get(self, request, **kwargs):
        raise Http404

    def post(self, request, **kwargs):
        return self.list(request, None, **kwargs)

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        servers = ServerCloud.objects.filter(is_active=True).order_by("price")
        # page = self.request.GET.get('page', '1')
        # pages = Paginator(servers, 20)
        # try:
        #     servers = pages.page(page)
        # except:
        #     servers = servers.filter(pk=-1)
        return servers


class ServerCloudBuy(LoginRequiredMixin, APIView):

    def post(self, request, slug):
        form = CreateServerCloudFrom(request.data)
        if not form.is_valid():
            return Response({'status': False, 'message': 'فرم را درست پر کنید'})
        server = get_object_or_404(ServerCloud, slug=slug)
        wallet = Wallet.objects.get(user=request.user)
        price_per_day = server.price_daily
        if wallet.amount < price_per_day:
            return Response({'status': False, 'message': 'شارژ حساب شما برای افزودن سرور کافی نیست'})
        operation_systems = server.os.filter(name=form.cleaned_data['os'])
        locations = server.location.filter(city=form.cleaned_data['location'])
        if len(operation_systems) < 1 or len(locations) < 1:
            return Response({'status': False, 'message': 'فرم را درست پر کنید'})
        last_server_rent = ServerRent.objects.last()
        name = "NetBach-" + str((last_server_rent.pk + 1) if last_server_rent else 0)
        client = get_datacenter(server)
        if client is None:
            return Response({'status': False, 'message': 'سرور یافت نشد'})

        res = client.server_create(
            name,
            server,
            form.cleaned_data['os'],
            form.cleaned_data['location']
        )
        if res["status"] is True:
            wallet.amount -= price_per_day
            wallet.save()
            server_created = res["server"]
            server_rent = ServerRent.objects.create(
                user=request.user,
                server=server,
                datacenter=server.datacenter,
                os=operation_systems.first(),
                location=locations.first(),
                token=server_created.token,
                username=server_created.username,
                password=server_created.password,
                slug=server_created.slug,
                name=server.name,
                ipv4=server_created.ipv4,
                ipv6=server_created.ipv6,
                cost=price_per_day,
                expire=datetime.datetime.now() + datetime.timedelta(days=1)
            )
            ServerCost.objects.create(
                user=request.user,
                server=server_rent,
                cost_amount=price_per_day,
                credit_amount=wallet.amount,
            )
            del res["server"]
            res["next"] = '/cloud' + reverse('server-info', urlconf='cloud.urls', args=[server_rent.slug])
            ActivityServer.objects.create(
                user=request.user,
                server=server_rent,
                activity='created'
            )
        return Response(res)


class ServerCloudRentViewSet(ViewSet):
    permission_classes = (IsAuthenticated, IsOwnerServer)
    lookup_field = "slug"

    @action(methods=["post"], detail=True)
    def reboot(self, request, slug):
        action_name = "reboot"
        server = get_object_or_404(ServerRent, user=request.user, slug=slug, is_active=True)
        self.check_object_permissions(request, server)
        datacenter = get_datacenter(server)
        if datacenter is None:
            return Response({"status": False, "message": "دیتاسنتر یافت نشد"})
        is_server_limit, ttl = is_server_limited(server, action_name)
        if is_server_limit:
            return Response({"status": False, "message": f"لطفا پس از {ttl} ثانیه دیگر دوباره تلاش کنید"})
        set_server_limit(server, action_name)
        response = datacenter.server_reboot(server)
        if response["status"] is True:
            ActivityServer.objects.create(
                user=request.user,
                server=server,
                activity=action_name
            )
        return Response(response)

    @action(methods=["post"], detail=True, url_path="power-on")
    def power_on(self, request, slug):
        action_name = "power_on"
        server = get_object_or_404(ServerRent, user=request.user, slug=slug, is_active=True)
        self.check_object_permissions(request, server)
        datacenter = get_datacenter(server)
        if datacenter is None:
            return Response({"status": False, "message": "دیتاسنتر یافت نشد"})
        is_server_limit, ttl = is_server_limited(server, action_name)
        if is_server_limit:
            return Response({"status": False, "message": f"لطفا پس از {ttl} ثانیه دیگر دوباره تلاش کنید"})
        set_server_limit(server, action_name)
        response = datacenter.server_power_on(server)
        if response["status"] is True:
            ActivityServer.objects.create(
                user=request.user,
                server=server,
                activity='on'
            )
        return Response(response)

    @action(methods=["post"], detail=True, url_path="power-off")
    def power_off(self, request, slug):
        action_name = "power_off"
        server = get_object_or_404(ServerRent, user=request.user, slug=slug, is_active=True)
        datacenter = get_datacenter(server)
        if datacenter is None:
            return Response({"status": False, "message": "دیتاسنتر یافت نشد"})
        is_server_limit, ttl = is_server_limited(server, action_name)
        if is_server_limit:
            return Response({"status": False, "message": f"لطفا پس از {ttl} ثانیه دیگر دوباره تلاش کنید"})
        set_server_limit(server, action_name)
        response = datacenter.server_power_off(server)
        if response["status"] is True:
            ActivityServer.objects.create(
                user=request.user,
                server=server,
                activity='off'
            )
        return Response(response)

    @action(methods=["post"], detail=True, url_path="change-ip")
    def change_ip(self, request, slug):
        action_name = "change_ip"
        server = get_object_or_404(ServerRent, user=request.user, slug=slug, is_active=True)
        datacenter = get_datacenter(server)
        if datacenter is None:
            return Response({"status": False, "message": "دیتاسنتر یافت نشد"})
        if server.datacenter.name.lower() != "hetzner":
            return Response({"status": False, "message": "تعویض آیپی برای این دیتاسنتر موجود نیست"})
        is_server_limit, ttl = is_server_limited(server, action_name)
        if is_server_limit:
            return Response({"status": False, "message": f"لطفا پس از {ttl} ثانیه دیگر دوباره تلاش کنید"})
        user_wallet = Wallet.objects.get(user=server.user)
        price_change_ip = 2500
        if user_wallet.amount < price_change_ip:
            return Response({"status": False, "message": f"موجودی شما کمتر از {price_change_ip} تومان میباشد"})
        set_server_limit(server, action_name)
        response = datacenter.server_change_ip(server)
        if response["status"] is True:
            user_wallet.amount -= price_change_ip
            server.ipv4 = response["ip"]
            server.cost += price_change_ip
            user_wallet.save()
            server.save()
            ServerCost.objects.create(
                user=request.user,
                server=server,
                cost_amount=price_change_ip,
                credit_amount=user_wallet.amount,
            )
            ActivityServer.objects.create(
                user=request.user,
                server=server,
                activity='change-ip'
            )
        return Response(response)

    @action(methods=["post"], detail=True, url_path="change-password")
    def change_password(self, request, slug):
        action_name = "change_password"
        server = get_object_or_404(ServerRent, user=request.user, slug=slug, is_active=True)
        self.check_object_permissions(request, server)
        datacenter = get_datacenter(server)
        if datacenter is None:
            return Response({"status": False, "message": "دیتاسنتر یافت نشد"})
        is_server_limit, ttl = is_server_limited(server, action_name)
        if is_server_limit:
            return Response({"status": False, "message": f"لطفا پس از {ttl} ثانیه دیگر دوباره تلاش کنید"})
        set_server_limit(server, action_name)
        response = datacenter.server_change_password(server)
        if response["status"] is True:
            server.password = response["password"]
            server.save()
            ActivityServer.objects.create(
                user=request.user,
                server=server,
                activity='change-passwd'
            )
        return Response(response)

    @action(methods=["post"], detail=True)
    def delete(self, request, slug):
        action_name = "delete"
        server = get_object_or_404(ServerRent, user=request.user, slug=slug, is_active=True)
        self.check_object_permissions(request, server)
        datacenter = get_datacenter(server)
        if datacenter is None:
            return Response({"status": False, "message": "دیتاسنتر یافت نشد"})
        is_server_limit, ttl = is_server_limited(server, action_name)
        if is_server_limit:
            return Response({"status": False, "message": f"لطفا پس از {ttl} ثانیه دیگر دوباره تلاش کنید"})
        set_server_limit(server, action_name)
        response = datacenter.server_delete(server)
        if response["status"] is True:
            server.is_active = False
            server.save()
            response["next"] = '/cloud' + reverse("server-list", urlconf="cloud.urls")
            ActivityServer.objects.create(
                user=request.user,
                server=server,
                activity=action_name
            )
        return Response(response)
