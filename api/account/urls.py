from django.conf.urls import include, url
from tastypie.api import Api
from .resources import AuthResource

gcm_api = Api(api_name='v1')
gcm_api.register(AuthResource())


urlpatterns = [
    url(r'^gcm/', include(gcm_api.urls)),
]