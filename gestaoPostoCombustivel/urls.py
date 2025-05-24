# faz os direcionamentos para o app gestaoPostoCombustivel

from django.urls import path
from gestaoPostoCombustivel import views # importar a view home

urlpatterns = [
    path('', views.index, name='index'), # rota para a view index

    path('venda', views.venda, name='venda'), # rota para a view venda

    path('reabastecer', views.reabastecer, name='reabastecer'), # rota para a view reabastecer

    path('relatorio', views.relatorio, name='relatorio'), # rota para a view relatorio


#ESTA É A ÚNICA LINHA NOVA QUE VOCÊ PRECISA ADICIONAR AO SEU ARQUIVO EXISTENTE 👇
    path('venda/processar/', views.registrar_venda_view, name='processar_venda_action'), # ROTA PARA PROCESSAR OS DADOS DO FORMULÁRIO DE VENDA
]