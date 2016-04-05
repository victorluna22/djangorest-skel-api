# encoding: utf-8

from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import FormMessageSerializer, FormCompanyMessageSerializer
from .models import FormMessage, FormCompanyMessage
from account.permissions import ConsumerPermission


class FormMessageViewSet(viewsets.ModelViewSet):
	queryset = FormMessage.objects.all().order_by('-id')
	serializer_class = FormMessageSerializer
	permission_classes = (IsAuthenticated,)

	def perform_create(self, serializer):
		serializer.save(user=self.request.user.get_user())


class FormCompanyMessageViewSet(viewsets.ModelViewSet):
	queryset = FormCompanyMessage.objects.all().order_by('-id')
	serializer_class = FormCompanyMessageSerializer
	permission_classes = (IsAuthenticated,)

	def perform_create(self, serializer):
		serializer.save(company=self.request.user.get_user())