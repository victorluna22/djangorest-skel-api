# encoding: utf-8

from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics
from rest_framework_jwt.settings import api_settings
from rest_framework import status
from rest_framework.exceptions import APIException
from django.contrib.gis.geos import GEOSGeometry
from ..serializers import ConsumerUserSerializer, AddressSerializer, AddressWriteSerializer, UserForgotPasswordSerializer, \
	UserChangePasswordSerializer
from ..models import ConsumerUser, AddressConsumerUser, Address, City, UserForgotPassword
from ..permissions import ConsumerPermission


class ConsumerUserViewSet(viewsets.ModelViewSet):
	queryset = ConsumerUser.objects.filter(is_active=1).order_by('-id')
	serializer_class = ConsumerUserSerializer
	filter_fields = ('email', 'facebook')
	# permission_classes = (IsAuthenticated, ConsumerPermission)

	def destroy(self, request, pk=None):
		if ConsumerUser.objects.filter(pk=pk).update(is_active=0):
			return Response({'detail': 'Registro removido com sucesso'})
		return Response({'detail': 'Erro ao tentar remover registro'})

	def delete_user(self, request, email=None):
		ConsumerUser.objects.get(email=email).delete()
		return Response({'detail': 'Registro removido com sucesso'})

	def create(self, request):
		request.data['email'] = request.data.get('email').lower()
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		user = serializer.save()

		jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
		jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
		payload = jwt_payload_handler(user)
		token = jwt_encode_handler(payload)

		data = serializer.data.copy()
		data.update({'token': token})

		headers = self.get_success_headers(data)
		return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class AddressUserCreateView(generics.CreateAPIView):
	serializer_class = AddressWriteSerializer
	permission_classes = (IsAuthenticated,)

	def post(self, request, *args, **kwargs):
		user = request.user.get_user()
		data = request.data.copy()

		lat = self.request.POST.get('lat')
		lon = self.request.POST.get('lon')
		if lat and lon:
			point = GEOSGeometry('POINT(%s %s)' % (lat, lon), srid=4326)
			data['location'] = point
		else:
			city_name = ''
			if data['city']:
				city = City.objects.get(pk=data['city'])
				city_name = city.name
			text_address = u'%s, %s, %s, %s' % (data['street'], data['number'], data['neighborhood'], city_name)
			result = Address.objects.geocodeGoogle(text_address.encode('utf8'))
			if result['results']:
				location = result['results'][0]['geometry']['location']
				point = GEOSGeometry('POINT(%s %s)' % (location['lat'], location['lng']), srid=4326)
				data['location'] = point

		serializer = AddressWriteSerializer(data=data)
		serializer.is_valid(raise_exception=True)
		address = serializer.save()

		AddressConsumerUser.objects.create(user=user, address=address, active=1)

		return Response(serializer.data)


class UserForgotPasswordView(generics.CreateAPIView):
	serializer_class = UserForgotPasswordSerializer

	def post(self, request, *args, **kwargs):
		email = request.data.get('email')
		serializer = UserForgotPasswordSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)

		if ConsumerUser.objects.filter(email=email).exists():
			user = ConsumerUser.objects.get(email=email)
			UserForgotPassword.objects.create(user=user)
			return Response({'message': 'Um email foi enviado para que você realizar a mudança da senha'})
		else:
			message = 'Email não encontrado'
			raise APIException(message)


class UserChangePasswordView(generics.CreateAPIView):
	serializer_class = UserChangePasswordSerializer

	def post(self, request, *args, **kwargs):
		hash = request.data.get('hash')
		password = request.data.get('password')
		serializer = UserChangePasswordSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)

		if ConsumerUser.objects.filter(requests_forgot__hash=hash).exists():
			user = ConsumerUser.objects.get(requests_forgot__hash=hash)
			user.set_password(password)
			user.save()
			return Response({'message': 'Mudança de senha efetuada com sucesso'})
		else:
			message = u'Usuário não encontrado'
			raise APIException(message)









user_delete = ConsumerUserViewSet.as_view({
    'delete': 'delete_user'
})