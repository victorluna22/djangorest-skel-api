# encoding: utf-8

from rest_framework import serializers
from django.conf import settings
from account.models import ConsumerUser, Employee
from account.serializers import AddressSerializer
from product.serializers import ProductSimpleSerializer
from company.models import Company
from company.serializers import CompanySerializer
from .models import Order, ProductItem, Discharge, BalanceOperation, PaymentType


class ProductItemSerializer(serializers.ModelSerializer):
    product = ProductSimpleSerializer(read_only=True)
    class Meta:
        model = ProductItem
        fields = ('id', 'order', 'product', 'qtd', 'price')

class ProductItemWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductItem
        fields = ('id', 'order', 'product', 'qtd', 'price')

class OrderWriteSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(label='Usuario', required=False, queryset=ConsumerUser.objects.all())
    total = serializers.DecimalField(max_digits=30, decimal_places=2, required=False)
    items = ProductItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ('id', 'user', 'company', 'billing_name', 'billing_number', 'billing_cpf', 'billing_expiration', 'billing_cvc', 'payment_type', 'total', 'status', 'address', 'items')

class OrderCashWriteSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(label='Usuario', required=False, queryset=ConsumerUser.objects.all())
    total = serializers.DecimalField(max_digits=30, decimal_places=2, required=False)
    items = ProductItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ('id', 'user', 'company', 'payment_type', 'return_cash_from', 'total', 'status', 'address', 'items')


class OrderReadSerializer(serializers.ModelSerializer):
    # situation = serializers.SerializerMethodField()
    company = CompanySerializer(read_only=True)
    address = AddressSerializer(read_only=True)
    items = ProductItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        depth = 1
        fields = ('id', 'user', 'company', 'billing_name', 'billing_number', 'billing_cpf', 'billing_expiration', 'billing_cvc', 'situation', 'payment_type', 'total', 'status', 'address', 'items', 'purchase_time')

    # def get_situation(self,obj):
    # 	return obj.get_situation

class OrderChangeSituationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('situation',)

class PaymentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentType
        fields = ('id', 'name')


class DischargeSerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(label='Empresa', required=False, queryset=Company.objects.all())
    pharmacist = serializers.PrimaryKeyRelatedField(label='Funcionario', required=False, queryset=Employee.objects.all())
    class Meta:
        model = Discharge
        depth = 1
        fields = ('id', 'company', 'pharmacist', 'value', 'status', 'owner_name', 'bank', 'agency', 'account', 'cpf', 'type_account', 'created_at', 'updated_at')
        read_only_fields = ('status', 'created_at', 'updated_at')

    def validate_value(self, value):
        if value <= settings.ADM_MIN_DISCHARGE:
            raise serializers.ValidationError("Valor inferior ao limite mínimo de %.2f reais." % settings.ADM_MIN_DISCHARGE)
        return value

class DischargeReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discharge
        depth = 1
        fields = ('id', 'company', 'pharmacist', 'value', 'status', 'owner_name', 'bank', 'agency', 'account', 'cpf', 'type_account', 'created_at', 'updated_at')
        read_only_fields = ('status', 'created_at', 'updated_at')


class DischargeStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discharge
        fields = ('id', 'status')


class BalanceOperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BalanceOperation
        depth = 1
        fields = ('id', 'company', 'order', 'discharge', 'kind', 'value', 'value_company', 'tax', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')


class RevenuesSerializer(serializers.Serializer):
    total = serializers.DecimalField(max_digits=10, decimal_places=2)
    receive = serializers.DecimalField(max_digits=10, decimal_places=2)
    transactions = serializers.IntegerField(min_value=0)
    date_created = serializers.DateField()







