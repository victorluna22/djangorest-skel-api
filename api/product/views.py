# encoding: utf-8

from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import views
from rest_framework.parsers import MultiPartParser,FormParser
from .serializers import ProductWriteSerializer, ProductReadSerializer, \
    ProductDetailSerializer, ProductChangeStatusSerializer, ProductRelatedSerializer
from .models import Product
from account.permissions import ConsumerPermission, CompanyPermission
from account.forms import FileForm
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductWriteSerializer
    permission_classes = (IsAuthenticated, CompanyPermission)

    def get_queryset(self):
        queryset = Product.objects.filter(deleted=0, company=self.request.user.get_user().company).order_by('-created_at')
        if self.request.GET.get('medicament_type'):
            queryset = queryset.filter(medicament_type=self.request.GET.get('medicament_type'))
        if self.request.GET.get('status'):
            queryset = queryset.filter(active=self.request.GET.get('status'))
        if self.request.GET.get('q'):
            queryset = queryset.filter(name__icontains=self.request.GET.get('q'))
        return queryset

    def destroy(self, request, pk=None):
    	if Product.objects.filter(pk=pk).update(deleted=1):
    		return Response({'detail': 'Registro removido com sucesso'})
    	return Response({'detail': 'Erro ao tentar remover registro'})

    def retrieve(self, request, pk=None):
        product = Product.objects.get(pk=pk)
        serializer = ProductDetailSerializer(product)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(company=self.request.user.get_user().company)

    def perform_update(self, serializer):
        serializer.save(company=self.request.user.get_user().company)



class ProductListCompany(generics.ListAPIView):
    serializer_class = ProductReadSerializer

    def get_queryset(self):
    	products = Product.objects.filter(active=1, deleted=0, company__deleted=0, company__active=1)

        company_id = self.request.GET.get('company_id')
        if company_id:
        	products = products.filter(company__id=company_id)

        name = self.request.GET.get('q')
        if name:
        	products = products.filter(name__icontains=name)

        medicament_type = self.request.GET.get('medicament_type')
        if medicament_type:
            types = medicament_type.split(',')
            products = products.filter(medicament_type__in=types)

        lat = self.request.GET.get('lat');lon = self.request.GET.get('lon');
        if lat and lon:
            point = 'POINT(%s %s)' % (lat, lon)
            pnt = GEOSGeometry(point, srid=4326)
            products = products.filter(company__address__location__distance_lte=(pnt, D(km=5)))

        order = self.request.GET.get('order') or 'distance'
        if order == 'medicament_type':
            products = products.order_by('medicament_type')
        elif order == 'lowest_price':
            products = products.order_by('price')
        elif order == 'distance' and lat and lon:
            products = products.distance(pnt, field_name='company__address__location').order_by('distance')

        limit = self.request.GET.get('limit') or 20

        return products[:limit]

class ProductImageView(views.APIView):
    permission_classes = (IsAuthenticated, CompanyPermission)
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        file_obj = request.data
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save()
        return Response({'file': 'http://domain.com.br/media/%s' % file.image.name})


class ProductStatusView(generics.ListAPIView):
    serializer_class = ProductChangeStatusSerializer
    permission_classes = (IsAuthenticated, CompanyPermission)

    def get(self, request, *args, **kwargs):
        product = Product.objects.get(pk=self.kwargs.get('pk'))
        product.active = not product.active
        product.save()
        return Response({'detail': 'Produto atualizado com sucesso'})

class ProductRelatedCreateView(generics.UpdateAPIView):
    serializer_class = ProductRelatedSerializer
    permission_classes = (IsAuthenticated, CompanyPermission)
    queryset = Product.objects.all()


# class ProductRelatedRemoveView(generics.DestroyAPIView):
#     permission_classes = (IsAuthenticated, CompanyPermission)
#     queryset = Product.objects.filter(deleted=0)

#     def perform_destroy(self, instance):
#         for id in self.request.data.getlist('products_related'):
#             instance.products_related.remove(id)

#     def destroy(self, request, *args, **kwargs):
#         super(ProductRelatedRemoveView, self).destroy(request, *args, **kwargs)
#         return Response({'detail': 'Produtos removidos com sucesso'})
