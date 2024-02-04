from django.contrib.auth import logout
from django.http import Http404
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http.response import JsonResponse
from django.core.paginator import Paginator
from config.settings import PAGINATION_HISTORY_LOGIN
from .forms import ProfileForm
from .models import User, Login
import jdatetime
import json
import re


@ensure_csrf_cookie
def user_login(request):
    if request.method != "GET":
        return Http404

    if request.user.is_authenticated:
        return redirect(reverse("home", urlconf="panel.urls"))
    return render(request, 'account/login.html')


def user_logout(request):
    if request.method != "GET":
        return Http404

    logout(request)
    return redirect("account:login")


@login_required()
def profile(request):
    if request.method == "GET":
        form = ProfileForm(initial={
            'first_name': request.user.first_name, 'last_name': request.user.last_name,
            'phone': request.user.phone, 'email': request.user.email, 'id_card': request.user.id_card,
            'zip_code': request.user.zip_code, 'address': request.user.address,
            'city': request.user.city, 'state': request.user.state
        })
        return render(request, "panel/profile.html", {"form": form})

    elif request.method == "POST":
        data = {"response": False, "message": "اطلاعات وارد شده صحیح نمی باشد."}
        form = ProfileForm(json.loads(request.body.decode("utf-8")))
        if not form.is_valid():
            return JsonResponse(data)
        user = get_object_or_404(User, pk=request.user.pk)
        cleaned_data = form.cleaned_data
        user.first_name = cleaned_data['first_name']
        user.last_name = cleaned_data['last_name']
        user.email = cleaned_data['email']
        user.city = cleaned_data['city']
        user.state = cleaned_data['state']
        user.address = cleaned_data['address']
        user.id_card = cleaned_data['id_card']
        user.zip_code = cleaned_data['zip_code']
        user.save()
        data["response"] = True
        data["message"] = 'پروفایل شما با موفقیت ویرایش شد.'
        return JsonResponse(data)


@login_required()
def login_history(request):
    login_histories = Login.objects.filter(user__pk=request.user.pk).order_by("-created")
    paginator = Paginator(login_histories, PAGINATION_HISTORY_LOGIN)
    page_number = request.GET.get("page", "1")
    try:
        page_obj = paginator.page(page_number)
    except Exception:
        return Http404
    for login in page_obj:
        data = ""
        results = re.findall("([L|l]inux|[W|w]indows|[M|m]ac)|([C|c]hrome|[F|f]irefox|[E|e]dge|[T|t]rident)", login.data)
        for result in results:
            for i in result:
                if i != "":
                    data += str(i).capitalize() + " , "
        login.data = data[:-2]
        login.created = jdatetime.datetime.fromgregorian(datetime=login.created).strftime('%H:%M:%S | %Y/%m/%d')
    return render(request, "panel/login-histories.html", {"logins": page_obj})
