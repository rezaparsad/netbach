import re

import jdatetime
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_list_or_404, redirect, render, get_object_or_404
from django.urls import reverse

from account.forms import EditTicketForm, CreateTicketForm
from account.models import Ticket, PackTicket
from account.utility import human_readable_size
from config.settings import PAGINATION_TRANSACTIONS, PAGINATION_INVOICES
from main.utility import get_date_persian
from wallet.gateway import ZarinPalRequest
from wallet.models import Wallet, ServerCost, ZarinPal


@login_required()
def home(request):
    return render(request, "panel/home.html")


@login_required()
def ticket_list(request):
    pack = PackTicket.objects.filter(user=request.user).order_by("-created")
    paginator = Paginator(pack, 25)
    page_number = request.GET.get("page", "1")
    try:
        sessions = paginator.page(page_number)
    except Exception:
        raise Http404
    choices = {}
    for choice in PackTicket.CHOICES_STATUS:
        choices[choice[0]] = choice[1]
    for session in sessions:
        session.ticket = Ticket.objects.filter(pack=session).last()
        session.updated = jdatetime.datetime.fromgregorian(datetime=session.ticket.created).strftime('%H:%M:%S | %Y/%m/%d')
        session.status_answer = choices.get(session.status)
    return render(request, 'panel/ticket-list.html', {'sessions': sessions})


@login_required()
def ticket_detail(request, pk):
    pack = get_object_or_404(PackTicket, user=request.user, pk=pk)
    tickets = get_list_or_404(Ticket, pack=pack)
    if request.method == 'POST':
        form = EditTicketForm(request.POST)
        if not form.is_valid():
            raise Http404
        pack = get_object_or_404(PackTicket, pk=pk)
        Ticket.objects.create(
            user=request.user,
            pack=pack,
            content=form.cleaned_data['content']
        )
        pack.status = "waiting_answer"
        pack.save()
        return redirect(reverse("ticket-list", urlconf="panel.urls"))

    choices = {}
    for choice in PackTicket.CHOICES_CATEGORY:
        choices[choice[0]] = choice[1]
    pack.status = choices.get(pack.category)

    for ticket in tickets:
        ticket_time = ticket.created
        ticket.created = get_date_persian(ticket_time)
        ticket.created += " ساعت "
        ticket.created += jdatetime.datetime.fromgregorian(datetime=ticket_time).strftime('%H:%M:%S')

    return render(
        request, 'panel/ticket-detail.html',
        {'tickets': tickets, 'pack_ticket': pack, 'form': EditTicketForm}
    )


@login_required()
def ticket_create(request):
    if request.method == 'POST':
        form = CreateTicketForm(request.POST)
        if not form.is_valid():
            raise Http404
        pack = PackTicket.objects.create(
            user=request.user,
            title=form.cleaned_data['title'],
            category=form.cleaned_data['category'],
            status="waiting_answer"
        )
        Ticket.objects.create(
            user=request.user,
            pack=pack,
            content=form.cleaned_data['content']
        )
        return redirect(reverse("ticket-detail", urlconf="panel.urls", args=[pack.pk]))
    return render(request, 'panel/ticket-create.html', {'form': CreateTicketForm})


@login_required()
def increase_credit(request):
    return render(request, "panel/increase-credit.html")


@login_required()
def transactions(request):
    user_transactions = ZarinPal.objects.filter(user__pk=request.user.pk).order_by("-created")
    variables = {True: "پرداخت شده", False: "لغو شده"}
    paginator = Paginator(user_transactions, PAGINATION_TRANSACTIONS)
    page_number = request.GET.get("page", "1")
    try:
        page_obj = paginator.page(page_number)
    except Exception:
        return Http404()
    for transaction in page_obj:
        transaction.amount = human_readable_size(transaction.amount, price=True)
        transaction.status_message = variables[transaction.is_success]
        transaction.created = jdatetime.datetime.fromgregorian(datetime=transaction.created).strftime('%H:%M:%S | %Y/%m/%d')
    return render(
        request, "panel/transactions.html", {"transactions": page_obj}
    )


@login_required()
def invoices(request):
    user_invoices = ServerCost.objects.filter(user=request.user).order_by("-created")
    paginator = Paginator(user_invoices, PAGINATION_INVOICES)
    page_number = request.GET.get("page", "1")
    try:
        page_obj = paginator.page(page_number)
    except Exception:
        return Http404()
    for invoice in page_obj:
        invoice.cost_amount = human_readable_size(invoice.cost_amount, price=True)
        invoice.credit_amount = human_readable_size(invoice.credit_amount, price=True)
        invoice.created = jdatetime.datetime.fromgregorian(datetime=invoice.created).strftime('%H:%M:%S | %Y/%m/%d')
    return render(
        request, "panel/invoices.html", {"invoices": page_obj}
    )


@login_required()
def callback_zarinpal(request, pk):
    zarinpal = get_object_or_404(ZarinPal, pk=pk)
    pal = ZarinPalRequest()
    response_verify = pal.verify(zarinpal.authority, int(zarinpal.amount))
    if response_verify.status and response_verify.code == 100:
        zarinpal.ref_id = response_verify.ref_id
        zarinpal.is_success = True
        wallet = Wallet.objects.get(user__pk=request.user.pk)
        wallet.amount += int(zarinpal.amount)
        wallet.save()
        zarinpal.save()
        return render(request, 'wallet/success_charge.html')
    return render(request, 'wallet/error_charge.html')
