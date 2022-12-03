from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, resolve

urls_without_email_confirmation = ['email_confirm', 'logout']


class CheckEmailStatus:
	def __init__(self, get_response):
		self._get_response = get_response

	def __call__(self, request):
		""" Check if user email is confirmed """
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
		"""If the user has exited the change email URLs, the keys that give access to the change email will be deleted"""
		session_keys = request.session.keys()

		if 'new_email' in session_keys:
			if resolve(request.path).url_name != 'email_change_confirm_new_email':
				del request.session['new_email']

		if 'access_change_email' in session_keys:
			if resolve(request.path).url_name != 'email_change_confirm':
				del request.session['access_change_email']

		response = self._get_response(request)
		return response
