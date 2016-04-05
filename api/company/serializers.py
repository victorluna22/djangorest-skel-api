# encoding: utf-8

from rest_framework import serializers
from account.serializers import ConsumerUserSerializer, AddressSerializer, AddressWriteSerializer
from account.models import Address
from checkout.models import PaymentType
from .models import Company, Review


class CompanySerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()
    address = AddressSerializer(required=False)
    # payment_types = serializers.PrimaryKeyRelatedField(many=True, queryset=PaymentType.objects.all(), read_only=False)
    class Meta:
        model = Company
        fields = ('id', 'name', 'cnpj', 'company_name', 'email', 'phone1', 'phone2', 'total', 'rating', 'address')
        read_only_fields = ('total', 'rating')

    def get_rating(self, obj):
        return obj.get_rating()


class CompanyWriteSerializer(serializers.ModelSerializer):
    address = AddressWriteSerializer(required=False)
    class Meta:
        model = Company
        fields = ('id', 'name', 'cnpj', 'company_name', 'email', 'phone1', 'phone2', 'address')

    def update(self, instance, data):
        if data.get('address'):
            address_data = data.pop('address')
            if instance.address:
                address = instance.address
            else:
                address = Address()

            # import pdb;pdb.set_trace()
            address.street = address_data.get('street', address.street)
            address.number = address_data.get('number', address.number)
            address.complement = address_data.get('complement', address.complement)
            address.neighborhood = address_data.get('neighborhood', address.neighborhood)
            address.city = address_data.get('city', None)
            address.cep = address_data.get('cep', address.cep)
            address.save()
            instance.address = address

        return super(CompanyWriteSerializer, self).update(instance, data)


class ReviewReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        depth = 1
        fields = ('id', 'user', 'company', 'vote', 'message', 'created_at')

class ReviewWriteSerializer(serializers.ModelSerializer):
    user = ConsumerUserSerializer(required=False)

    class Meta:
        model = Review
        fields = ('id', 'user', 'company', 'vote', 'message')

