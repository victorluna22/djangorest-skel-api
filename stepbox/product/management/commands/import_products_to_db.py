# encoding: utf-8

import csv
from decimal import Decimal
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.utils import translation
from product.models import ProductBase

class Command(BaseCommand):

	def handle(self, *args, **options):
		count = 0
		with open('static/medicamentos.csv') as f:
			reader = csv.reader(f, delimiter=';')
			for row in reader:
				count += 1
				if count < 5:
					continue
				# import pdb;pdb.set_trace()
				if not ProductBase.objects.filter(codigo_ggrem=row[3], registro=row[4]).exists():

					try: row[9] = Decimal(row[9].replace(',', '.') or 0)
					except: row[9] = 0
					try: row[10] = Decimal(row[10].replace(',', '.') or 0)
					except: row[10] = 0
					try: row[11] = Decimal(row[11].replace(',', '.') or 0)
					except: row[11] = 0
					try: row[12] = Decimal(row[12].replace(',', '.') or 0)
					except: row[12] = 0
					try: row[13] = Decimal(row[13].replace(',', '.') or 0)
					except: row[13] = 0
					try: row[14] = Decimal(row[14].replace(',', '.') or 0)
					except: row[14] = 0
					try: row[15] = Decimal(row[15].replace(',', '.') or 0)
					except: row[15] = 0
					try: row[16] = Decimal(row[16].replace(',', '.') or 0)
					except: row[16] = 0
					try: row[17] = Decimal(row[17].replace(',', '.') or 0)
					except: row[17] = 0
					try: row[18] = Decimal(row[18].replace(',', '.') or 0)
					except: row[18] = 0
					try: row[19] = Decimal(row[19].replace(',', '.') or 0)
					except: row[19] = 0
					try: row[20] = Decimal(row[20].replace(',', '.') or 0)
					except: row[20] = 0



					p = ProductBase.objects.create(
					    principio_ativo=row[0],
					    cnpj=row[1],
					    laboratorio=row[2],
					    codigo_ggrem=row[3],
					    registro=row[4],
					    ean=row[5],
					    produto=row[6],
					    apresentacao=row[7],
					    classe_terapeutica=row[8],
					    pf0=row[9],
					    pf12=row[10],
					    pf17=row[11],
					    pf18=row[12],
					    pf19=row[13],
					    pf17_manaus=row[14],
					    pmc0=row[15],
					    pmc12=row[16],
					    pmc17=row[17],
					    pmc18=row[18],
					    pmc19=row[19],
					    pmc17_manaus=row[20],
					    restricao_hospitalar=row[21] == 'Sim',
					    cap=row[22] == 'Sim',
					    confaz_87=row[23] == 'Sim',
					    analise_recursal=row[24],
					    ultima_alteracao=datetime.strptime(row[25], '%d/%m/%Y'),
					    )
				print count

