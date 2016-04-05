# encoding: utf-8
import datetime
from django.utils import timezone
from rest_framework import serializers
from company.models import Company
from .models import ConsumerUser, Employee, AdmUser, State, City, Address, UserForgotPassword


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        depth = 1
        fields = ('id', 'name', 'state')

class AddressSerializer(serializers.ModelSerializer):
    lat = serializers.SerializerMethodField()
    lon = serializers.SerializerMethodField()
    city = CitySerializer()
    class Meta:
        model = Address
        fields = ('id', 'street', 'number', 'complement', 'neighborhood', 'city', 'cep', 'location', 'lat', 'lon')

    def get_lat(self, obj):
        if obj.location:
            return obj.location.x 

    def get_lon(self, obj):
        if obj.location:
            return obj.location.y


class AddressWriteSerializer(serializers.ModelSerializer):
    # lat = serializers.SerializerMethodField()
    # lon = serializers.SerializerMethodField()
    class Meta:
        model = Address
        fields = ('id', 'street', 'number', 'complement', 'neighborhood', 'city', 'cep', 'location')


class ConsumerUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=False)
    address = AddressSerializer(many=True, read_only=True)
    class Meta:
        model = ConsumerUser
        depth = 1
        fields = ('id', 'full_name', 'email', 'password', 'facebook', 'birthday', 'gender', 'phone', 'address')

    def update(self, attrs, instance=None):
        user = super(ConsumerUserSerializer, self).update(attrs, instance)
        if instance.get('password'):
            user.set_password(attrs.password)
            user.save()
        return user



class EmployeeSerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(label='Empresa', required=False, queryset=Company.objects.all())
    password = serializers.CharField(required=False)
    class Meta:
        model = Employee
        fields = ('id', 'full_name', 'email', 'company', 'password')

    def update(self, attrs, instance=None):
        user = super(EmployeeSerializer, self).update(attrs, instance)
        if instance.get('password'):
            user.set_password(attrs.password)
            user.save()
        return user



class AdmUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=False)
    class Meta:
        model = AdmUser
        fields = ('id', 'full_name', 'email', 'password')

    def update(self, attrs, instance=None):
        user = super(AdmUserSerializer, self).update(attrs, instance)
        if instance.get('password'):
            user.set_password(attrs.password)
            user.save()
        return user



class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ('id', 'name', 'acronym')

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ('id', 'name', 'state')


class UserForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=150)


class UserChangePasswordSerializer(serializers.Serializer):
    hash = serializers.UUIDField(format='hex_verbose')
    password = serializers.CharField(max_length=30)

    def validate(self, data):
        if UserForgotPassword.objects.filter(hash=data['hash']).exists():
            forgot_pwd = UserForgotPassword.objects.get(hash=data['hash'])
            if forgot_pwd.created_at + datetime.timedelta(days=1) < timezone.now():
                raise serializers.ValidationError("O prazo para mudar a senha por esse link expirou. Você precisa solicitar novamente.")
        return data





