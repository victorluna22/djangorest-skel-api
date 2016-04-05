# encoding: utf-8

from rest_framework import serializers
from .models import FormMessage, FormCompanyMessage


class FormMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormMessage
        depth = 1
        fields = ('id', 'user', 'subject', 'message', 'created_at')


class FormCompanyMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormCompanyMessage
        depth = 1
        fields = ('id', 'company', 'subject', 'message', 'created_at')