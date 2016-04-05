# encoding: utf-8

import urllib, json
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry
from geopy.geocoders import Nominatim, GoogleV3
from account.permissions import ConsumerPermission
from ..serializers import StateSerializer, CitySerializer, AddressSerializer, AddressWriteSerializer
from ..models import State, City, Address, AddressConsumerUser


class StateViewSet(viewsets.ModelViewSet):
    queryset = State.objects.all().order_by('-id')
    serializer_class = StateSerializer

class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all().order_by('-id')
    serializer_class = CitySerializer

class AddressViewSet(viewsets.ModelViewSet):
	queryset = Address.objects.filter(deleted=0).order_by('-id')
	serializer_class = AddressSerializer
	permission_classes = (IsAuthenticated, ConsumerPermission)


	def perform_create(self, serializer):
		lat = self.request.POST.get('lat')
		lon = self.request.POST.get('lon')
		point = GEOSGeometry('POINT(%s %s)' % (lat, lon), srid=4326)
		serializer.save(location=point)

	def destroy(self, request, pk=None):
		address = AddressConsumerUser.objects.get(address__id=pk, user=self.request.user.get_user())
		try:
			address.delete()
			return Response({'detail': 'Registro removido com sucesso'})
		except:
			return Response({'detail': 'Erro ao tentar remover registro'})


class GetGeoLocation(APIView):

	def get(self, request, format=None):
		data = Address.objects.geocodeCorreios(request.GET.get('cep'))
		city = City.objects.filter(state__acronym=data['uf'], name=data['localidade'])
		if city:
			data['city'] = city[0].id
		else:
			state = State.objects.get(acronym=data['uf'])
			city = City.objects.create(state=state, name=data['localidade'])
			data['city'] = city.id
		return Response(data)

class GetGeoLocationByLatLon(APIView):

	def get(self, request, format=None):
		if request.GET.get('lat') and request.GET.get('lon'):
			data = Address.objects.geocoderGeoPyLatLon(request.GET.get('lat'), request.GET.get('lon'))
			city = City.objects.filter(state__acronym=data['state'], name=data['city'])
			if city:
				data['city_id'] = city[0].id
			else:
				state = State.objects.get(acronym=data['state'])
				city = City.objects.create(state=state, name=data['city'])
				data['city_id'] = city.id
			return Response(data)
		return Response({'detail': 'Latitude e Longitude são campos obrigatórios'})
		

	
		