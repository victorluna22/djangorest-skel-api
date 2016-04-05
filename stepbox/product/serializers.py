# encoding: utf-8

from rest_framework import serializers
from django.contrib.gis.geos import Point, GEOSGeometry
from company.serializers import CompanySerializer
from company.models import Company
from .models import Product


class ProductWriteSerializer(serializers.ModelSerializer):
	company = serializers.PrimaryKeyRelatedField(label='Empresa', required=False, queryset=Company.objects.all())
	class Meta:
		model = Product
		fields = ('id', 'name', 'company', 'price', 'type', 'medicament_type', 'manufacturer', 'products_related', 'available', 'active', 'obs', 'image')


class ProductReadSerializer(serializers.ModelSerializer):
	distance = serializers.SerializerMethodField()
	company = CompanySerializer(read_only=True)
	class Meta:
		model = Product
		depth = 2
		fields = ('id', 'name', 'company', 'price', 'type', 'medicament_type', 'manufacturer', 'available', 'obs', 'image', 'active', 'distance')

	def get_distance(self, obj):
		lat = self.context['request'].GET.get('lat')
		lon = self.context['request'].GET.get('lon')
		if lat and lon:
			mobile_point = GEOSGeometry('SRID=4326;POINT(%s %s)' % (lat, lon))
			company_point = GEOSGeometry('SRID=4326;POINT(%s %s)' % (obj.company.address.location.x, obj.company.address.location.y))
			distance = mobile_point.distance(company_point) * 100
			return "%.2f" % distance
		return None


class ProductDetailSerializer(serializers.ModelSerializer):
	class Meta:
		model = Product
		depth = 2
		fields = ('id', 'name', 'company', 'price', 'type', 'medicament_type', 'manufacturer', 'available', 'obs', 'image', 'products_related', 'active')



class ProductChangeStatusSerializer(serializers.ModelSerializer):
	class Meta:
		model = Product
		fields = ('active',)

class ProductRelatedSerializer(serializers.ModelSerializer):
	class Meta:
		model = Product
		fields = ('id', 'products_related')

class ProductSimpleSerializer(serializers.ModelSerializer):
	class Meta:
		model = Product
		fields = ('id', 'name', 'company', 'price', 'type', 'medicament_type', 'manufacturer', 'available', 'obs', 'image', 'active')
