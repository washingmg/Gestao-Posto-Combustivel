# gestaoPostoCombustivel/views.py

from django.shortcuts import render, redirect
from django.http import HttpResponse 
from django.db import transaction
from django.contrib import messages
from decimal import Decimal, InvalidOperation

from .models import (
    Venda,
    Tanque,
    Bomba,
    PrecoCombustivel,
    PAGAMENTO_CHOICES
)

def index(request):
    """
    Página inicial. Pode mostrar um resumo dos níveis dos tanques.
    Precisa ser adaptada para a nova estrutura de Tanques.
    """
    tanques = Tanque.objects.select_related('combustivel').all().order_by('combustivel__id_combustivel')
    
    bombas_com_tanques = []
    for bomba_obj in Bomba.objects.prefetch_related('combustiveis_disponiveis__tanque').all().order_by('id_bomba'):
        info_bomba = {'nome': str(bomba_obj), 'combustiveis': []}
        for combustivel_preco_obj in bomba_obj.combustiveis_disponiveis.all():
            try:

                tanque_obj = combustivel_preco_obj.tanque 
                info_bomba['combustiveis'].append({
                    'tipo': combustivel_preco_obj.get_id_combustivel_display(),
                    'quantidade_disponivel': float(tanque_obj.quantidade_disponivel),
                    'capacidade_maxima': float(tanque_obj.capacidade_maxima) if tanque_obj.capacidade_maxima else 0.0,
                    'percentual': float(round((tanque_obj.quantidade_disponivel / tanque_obj.capacidade_maxima) * 100, 1)) if tanque_obj.capacidade_maxima and tanque_obj.capacidade_maxima > 0 else 0.0
                })
            except Tanque.DoesNotExist:
                 info_bomba['combustiveis'].append({
                    'tipo': combustivel_preco_obj.get_id_combustivel_display(),
                    'quantidade_disponivel': 'Tanque não cadastrado',
                    'capacidade_maxima': 0.0,
                    'percentual': 0.0
                })
        bombas_com_tanques.append(info_bomba)

    context = {
        'info_bombas_tanques': bombas_com_tanques,
         'bombas': bombas_com_tanques, 
    }
    return render(request, 'index.html', context)


def venda(request):
    """
    Exibe o formulário de venda.
    Popula os dropdowns de bombas e combustíveis a partir dos modelos.
    """
    lista_de_bombas = Bomba.objects.all().order_by('id_bomba')
    lista_de_combustiveis = PrecoCombustivel.objects.all().order_by('id_combustivel')

    context = {
        'lista_de_bombas': lista_de_bombas,
        'lista_de_combustiveis': lista_de_combustiveis,
        'formas_de_pagamento': PAGAMENTO_CHOICES,
    }
    return render(request, 'venda.html', context)


def registrar_venda_view(request):
    """
    Processa os dados do formulário de venda, calcula o valor,
    cria o registro de Venda e atualiza o estoque no Tanque.
    """
    if request.method == 'POST':
        bomba_id_selecionada = request.POST.get('bomba_selecionada') 
        combustivel_id_selecionado = request.POST.get('tipo_combustivel') 
        quantidade_vendida_str = request.POST.get('quantidade_litros')
        forma_pagamento_selecionada = request.POST.get('forma_pagamento')

        if not all([bomba_id_selecionada, combustivel_id_selecionado, quantidade_vendida_str, forma_pagamento_selecionada]):
            messages.error(request, "Todos os campos obrigatórios devem ser preenchidos!")
            return redirect('venda') 

        try:
            quantidade_vendida = Decimal(quantidade_vendida_str)
            if quantidade_vendida <= 0:
                messages.error(request, "A quantidade vendida deve ser maior que zero.")
                return redirect('venda')
        except InvalidOperation:
            messages.error(request, "Quantidade inválida. Use um número válido.")
            return redirect('venda')

        try:
            with transaction.atomic():
                # Buscar os objetos Bomba e PrecoCombustivel (que representa o tipo de combustível)
                bomba_obj = Bomba.objects.get(id_bomba=bomba_id_selecionada)
                combustivel_obj = PrecoCombustivel.objects.get(id_combustivel=combustivel_id_selecionado)

                # Verificar se a bomba selecionada pode dispensar o combustível selecionado
                if not bomba_obj.combustiveis_disponiveis.filter(id_combustivel=combustivel_obj.id_combustivel).exists():
                    messages.error(request, f"A Bomba {bomba_obj} não dispensa o combustível {combustivel_obj.get_id_combustivel_display()}.")
                    return redirect('venda')

                # Buscar o tanque para o tipo de combustível selecionado
                tanque_do_combustivel = Tanque.objects.get(combustivel=combustivel_obj) # combustivel é a pk de Tanque

                # Verificar quantidade disponível no tanque
                if tanque_do_combustivel.quantidade_disponivel < quantidade_vendida:
                    messages.error(request, f"Estoque insuficiente de {combustivel_obj.get_id_combustivel_display()}. Disponível: {tanque_do_combustivel.quantidade_disponivel}L.")
                    return redirect('venda')

                # Calcular o valor total
                preco_unitario = combustivel_obj.preco_por_litro
                valor_total_calculado = (preco_unitario * quantidade_vendida).quantize(Decimal('0.01'))

                # Criar o registro de Venda
                Venda.objects.create(
                    bomba=bomba_obj,             
                    combustivel=combustivel_obj, 
                    quantidade=quantidade_vendida,
                    pagamento=forma_pagamento_selecionada,
                    valor=valor_total_calculado
                )

                # Atualizar a quantidade_disponivel no Tanque
                tanque_do_combustivel.quantidade_disponivel -= quantidade_vendida
                tanque_do_combustivel.save()

                messages.success(request,
                    f"Venda de {quantidade_vendida}L de {combustivel_obj.get_id_combustivel_display()} "
                    f"(R$ {valor_total_calculado}) na Bomba {bomba_obj} registrada com sucesso! Estoque atualizado."
                )
                return redirect('venda')

        except Bomba.DoesNotExist:
            messages.error(request, f"Bomba '{bomba_id_selecionada}' não encontrada.")
            return redirect('venda')
        except PrecoCombustivel.DoesNotExist:
            messages.error(request, f"Combustível '{combustivel_id_selecionado}' não encontrado.")
            return redirect('venda')
        except Tanque.DoesNotExist:
            messages.error(request, f"Não há tanque de estoque cadastrado para o combustível {combustivel_id_selecionado}.")
            return redirect('venda')
        except Exception as e:
            messages.error(request, f"Ocorreu um erro inesperado ao processar a venda: {e}")
            return redirect('venda')
    else:
        return redirect('venda')


def reabastecer(request):
    """
    Exibe o formulário de reabastecimento e processa os dados.
    """
    tanques = Tanque.objects.select_related('combustivel').all().order_by('combustivel__id_combustivel')
    
    if request.method == 'POST':
        combustivel_id = request.POST.get('combustivel')
        quantidade_str = request.POST.get('quantidade')
        
        if not all([combustivel_id, quantidade_str]):
            messages.error(request, "Todos os campos obrigatórios devem ser preenchidos!")
            return redirect('reabastecer')
        
        try:
            quantidade = Decimal(quantidade_str)
            if quantidade <= 0:
                messages.error(request, "A quantidade deve ser maior que zero.")
                return redirect('reabastecer')
        except InvalidOperation:
            messages.error(request, "Quantidade inválida. Use um número válido.")
            return redirect('reabastecer')
        
        try:
            with transaction.atomic():
                tanque = Tanque.objects.select_for_update().get(combustivel_id=combustivel_id)
                capacidade_disponivel = tanque.capacidade_maxima - tanque.quantidade_disponivel
                
                if quantidade > capacidade_disponivel:
                    messages.error(
                        request,
                        f"Quantidade excede a capacidade disponível. "
                        f"Máximo possível: {capacidade_disponivel:.2f}L"
                    )
                    return redirect('reabastecer')
                
                tanque.quantidade_disponivel += quantidade
                tanque.save()
                
                messages.success(
                    request,
                    f"Tanque de {tanque.combustivel.get_id_combustivel_display()} reabastecido com {quantidade}L. "
                    f"Novo nível: {tanque.quantidade_disponivel:.2f}L/{tanque.capacidade_maxima:.2f}L"
                )
                return redirect('reabastecer')
                
        except Tanque.DoesNotExist:
            messages.error(request, "Tanque não encontrado.")
            return redirect('reabastecer')
        except Exception as e:
            messages.error(request, f"Ocorreu um erro ao reabastecer: {str(e)}")
            return redirect('reabastecer')
    
    context = {
        'tanques': tanques,
    }
    return render(request, 'reabastecer.html', context)

def relatorio(request):
    """
    Exibe um relatório de vendas e o status atual dos tanques.
    """
    vendas = Venda.objects.select_related('bomba', 'combustivel').all().order_by('-data')
    receita_total = sum(venda.valor for venda in vendas) # sum() funciona com Decimal

    # Para status do estoque, agora buscamos dos Tanques
    status_tanques = Tanque.objects.select_related('combustivel').all().order_by('combustivel__id_combustivel')

    context = {
        'vendas': vendas,
        'receita_total': receita_total,
        'status_tanques': status_tanques,
    }
    return render(request, 'relatorio.html', context)
