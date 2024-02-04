from config.settings import LOGIN_URL, API_URL, DOMAIN_URL


def site_context(request):
    return {'domain_url': DOMAIN_URL, 'login_url': LOGIN_URL, 'api_url': API_URL}
