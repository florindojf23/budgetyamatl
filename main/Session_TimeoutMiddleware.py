from django.utils import timezone
import logging
logger = logging.getLogger(__name__)

class SessionTimeoutMiddleware:
	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		if request.session.modified:
			logger.info('Session modified at: %s', timezone.now())
			request.session['_session_last_activity'] = str(timezone.now())
			# if :
				# pass
		response = self.get_response(request)
		return response