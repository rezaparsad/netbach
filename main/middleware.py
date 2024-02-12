class CustomMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try: 
            del response['X-Robots-Tag']
        except:
            pass
        return response