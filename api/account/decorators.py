from django.http import HttpResponseRedirect

def typeuser_only(types):
	def method_wrapper(function):
		def wrap(request, *args, **kwargs):
			if hasattr(request.user.get_user(), 'type') and request.user.get_user().type in types:
				return function(request, *args, **kwargs)
			else:
				return HttpResponseRedirect('/')
		wrap.__doc__=function.__doc__
		wrap.__name__=function.__name__
		return wrap
	return method_wrapper

