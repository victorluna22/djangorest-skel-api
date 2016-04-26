# encoding: utf-8

from itertools import chain
from django.shortcuts import render
from django.contrib.gis.geos import GEOSGeometry
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import APIException
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from .serializers import CompanySerializer, CompanyWriteSerializer, ReviewWriteSerializer, ReviewReadSerializer
from .models import Company, Review
from account.serializers import AddressSerializer, AddressWriteSerializer
from checkout.serializers import PaymentTypeSerializer
from account.permissions import ConsumerPermission, CompanyPermission
from account.models import Address, City
from checkout.models import ProductItem, PaymentType


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.filter(deleted=0).order_by('-id')
    serializer_class = CompanySerializer
    # permission_classes = (IsAuthenticated, ConsumerPermission)

    def update(self, request, pk=None):
        self.serializer_class = CompanyWriteSerializer
        return super(CompanyViewSet, self).update(request, pk)

    def destroy(self, request, pk=None):
        if Company.objects.filter(pk=pk).update(deleted=1):
            return Response({'detail': 'Registro removido com sucesso'})
        return Response({'detail': 'Erro ao tentar remover registro'})


class CompanyEditView(generics.UpdateAPIView):
    serializer_class = CompanyWriteSerializer
    permission_classes = (IsAuthenticated, CompanyPermission)
    queryset = Company.objects.all()

    def get_object(self):
        return self.request.user.get_user().company


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all().order_by('-id')
    serializer_class = ReviewWriteSerializer

    def get_permissions(self):
        if self.action in ('create',):
            self.permission_classes = [IsAuthenticated, ConsumerPermission]
        else:
            self.permission_classes = [IsAuthenticated, CompanyPermission]
        return super(self.__class__, self).get_permissions()

    def perform_create(self, serializer):
        user = self.request.user.get_user()
        serializer.save(user=user)

    def list(self, request):
        company_user = self.request.user.get_user()
        queryset = Review.objects.filter(company=company_user.company)
        serializer = ReviewReadSerializer(queryset, many=True)
        return Response(serializer.data)



class AddressCompanyCreateView(generics.CreateAPIView):
    serializer_class = AddressSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        company_user = request.user.get_user()
        if not company_user.is_company():
            message = 'É necessário ser funcionário para efetuar esta operação'
            raise APIException(message)
        company = company_user.company

        lat = self.request.POST.get('lat')
        lon = self.request.POST.get('lon')
        if lat and lon:
            point = GEOSGeometry('POINT(%s %s)' % (lat, lon), srid=4326)
            request.data['location'] = point
        else:
            city_name = ''
            if request.data['city']:
                city = City.objects.get(pk=request.data['city'])
                city_name = city.name
            text_address = u'%s, %s, %s, %s' % (request.data['street'], request.data['number'], request.data['neighborhood'], city_name)
            data = Address.objects.geocodeGoogle(text_address.encode('utf8'))
            if data['results']:
                location = data['results'][0]['geometry']['location']
                point = GEOSGeometry('POINT(%s %s)' % (location['lat'], location['lng']), srid=4326)
                request.data['location'] = point

        if company.address:
            serializer = AddressWriteSerializer(company.address, data=request.data)
        else:
            serializer = AddressWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        address = serializer.save()

        if not company.address:
            company.address = address
            company.save()

        return Response(serializer.data)


class CompanyChangeStatusView(APIView):
    permission_classes = (IsAuthenticated,)
    queryset = Company.objects.all()

    def get(self, request, *args, **kwargs):
        company = Company.objects.get(pk=self.kwargs.get('pk'))
        company.active = not company.active
        company.save()
        serializer = CompanySerializer(instance=company)

        return Response(serializer.data)

class CompanyDashInfoView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = request.user.get_user()
        data = {}
        data['best_seller'] = ProductItem.objects.get_best_seller(user.company)
        return Response(data)


class CompanyPaymentsView(generics.ListAPIView):
    serializer_class = PaymentTypeSerializer
    permission_classes = (IsAuthenticated, ConsumerPermission)

    def get_queryset(self):
        # import pdb;pdb.set_trace()
        obligatories = PaymentType.objects.filter(obligatory=True)
        company = Company.objects.get(id=self.kwargs.get('pk'))
        from_company = company.payment_types.all()

        return chain(obligatories, from_company)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({'id': self.kwargs.get('pk'), 'payment_types': serializer.data})









