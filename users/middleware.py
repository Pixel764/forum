from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, resolve

urls_without_email_confirmation = ['email_confirm', 'logout']


class CheckEmailStatus:
    def __init__(self, get_response):
        self._get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if resolve(request.path).url_name in urls_without_email_confirmation:
                pass
            elif not request.user.email_confirmed:
                return HttpResponseRedirect(reverse_lazy('users:email_confirm', kwargs={'status': 'confirm'}))
        response = self._get_response(request)
        return response


class EmailChangeAccess:
    def __init__(self, get_response):
        self._get_response = get_response

    def __call__(self, request):
        session_keys = request.session.keys()
        if 'new_email' in session_keys:
            if resolve(request.path).url_name != 'email_change_confirm_new_email':
                del request.session['new_email']
        if 'access_change_email' in session_keys and request.session['access_change_email']:
            if resolve(request.path).url_name != 'email_change_confirm':
                request.session['access_change_email'] = False
        response = self._get_response(request)
        return response
