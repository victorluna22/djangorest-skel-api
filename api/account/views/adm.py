# encoding: utf-8

from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from ..serializers import AdmUserSerializer
from ..models import AdmUser


class AdmUserViewSet(viewsets.ModelViewSet):
    queryset = AdmUser.objects.filter(is_active=1).order_by('-id')
    serializer_class = AdmUserSerializer

    def destroy(self, request, pk=None):
    	if AdmUser.objects.filter(pk=pk).update(is_active=0):
    		return Response({'detail': 'Registro removido com sucesso'})
    	return Response({'detail': 'Erro ao tentar remover registro'})