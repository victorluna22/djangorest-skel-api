# encoding: utf-8

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from rest_framework import parsers, renderers
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework_jwt.views import JSONWebTokenAPIView, JSONWebTokenSerializer, RefreshJSONWebToken
from rest_framework_jwt.settings import api_settings
from ..models import CONSUMER, COMPANY, ADM, DeviceUser
from ..serializers import ConsumerUserSerializer, EmployeeSerializer, AdmUserSerializer
from ..decorators import typeuser_only
import time

jwt_response_payload_handler = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER

''' User Controller's views  '''
class ConsumerRequired(object):
    @method_decorator(login_required)
    @method_decorator(typeuser_only(types=[CONSUMER]))
    def dispatch(self, *args, **kwargs):
        return super(ConsumerRequired, self).dispatch(*args, **kwargs)
    def get_context_data(self, *args, **kwargs):
        context = super(ConsumerRequired, self).get_context_data(*args, **kwargs)
        context['title'] = self.kwargs.get('title')
        return context

class CompanyRequired(object):
    @method_decorator(login_required)
    @method_decorator(typeuser_only(types=[COMPANY]))
    def dispatch(self, *args, **kwargs):
        return super(CompanyRequired, self).dispatch(*args, **kwargs)
    def get_context_data(self, *args, **kwargs):
        context = super(CompanyRequired, self).get_context_data(*args, **kwargs)
        context['title'] = self.kwargs.get('title')
        return context

class AdmRequired(object):
    @method_decorator(login_required)
    @method_decorator(typeuser_only(types=[ADM]))
    def dispatch(self, *args, **kwargs):
        return super(AdmRequired, self).dispatch(*args, **kwargs)
    def get_context_data(self, *args, **kwargs):
        context = super(AdmRequired, self).get_context_data(*args, **kwargs)
        context['title'] = self.kwargs.get('title')
        return context

class ObtainAuthToken(JSONWebTokenAPIView):
    serializer_class = JSONWebTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data
        )

        if serializer.is_valid(raise_exception=True):
            user = serializer.object.get('user') or request.user
            token = serializer.object.get('token')
            response_data = jwt_response_payload_handler(token, user, request)
            if user.get_user().is_consumer():
                s = ConsumerUserSerializer(user.get_user())
                data = request.data
                if data.get('gcm_token'):
                    print 'IFFFFFF - %s' % data.get('gcm_token')
                    if not DeviceUser.objects.filter(reg_id=data.get('gcm_token'), user=user.get_user()).exists():
                        DeviceUser.objects.create(reg_id=data.get('gcm_token'), user=user.get_user(), dev_id=time.time(), name=user.get_user().get_full_name(), is_active=1)
            elif user.get_user().is_company():
                if user.get_user().company.deleted == 1 or user.get_user().company.active == 0:
                    raise APIException(u'Empresa inativa.')
                s = EmployeeSerializer(user.get_user())
            else:
                s = AdmUserSerializer(user.get_user())
            response_data['user'] = s.data
            return Response(response_data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RefreshAuthToken(RefreshJSONWebToken):

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data
        )

        if serializer.is_valid():
            user = serializer.object.get('user') or request.user
            token = serializer.object.get('token')
            response_data = jwt_response_payload_handler(token, user, request)
            s = ConsumerUserSerializer(user.get_user())
            response_data['user'] = s.data
            return Response(response_data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



def home(request):
    return HttpResponse('')