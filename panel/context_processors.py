from django.contrib.humanize.templatetags import humanize

from account.utility import get_user_agent
from config.settings import CLOUD_URL, PANEL_URL, DOMAIN_URL
from wallet.models import Wallet


def site_context(request):
    amount = "0"
    if request.user.is_authenticated:
        try:
            wallet = Wallet.objects.get(user__pk=request.user.pk)
            amount = humanize.intcomma(wallet.amount)
        except Exception:
            amount = "0"
    user_agent = get_user_agent(request)
    is_mobile = True if 'mobile' in user_agent else False
    return {'PANEL_URL': PANEL_URL, 'cloud_url': CLOUD_URL, 'current_credit': amount,
            "is_mobile": is_mobile, 'domain_url': DOMAIN_URL}
