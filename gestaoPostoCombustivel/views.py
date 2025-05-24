# seu_app/views.py
from django.shortcuts import render, redirect # redirect pode ser novo
from django.http import HttpResponse
from django.db import transaction    # IMPORTANTE: para transações atômicas
from django.contrib import messages  # IMPORTANTE: para feedback ao usuário
from decimal import Decimal, InvalidOperation
from .models import Venda, Estoque, PrecoCombustivel # Adicionado PrecoCombustivel aqui
from collections import defaultdict # Importe se ainda não estiver importado

# cada view vai ser uma função (no momento) que vai dizer o que vai ser feita, quando a requisição for feita

def index(request):
    estoques = Estoque.objects.all().order_by('bomba')

    bombas_info = defaultdict(list)
    for estoque_item in estoques: # Renomeei para evitar conflito com o modelo Estoque
        bombas_info[f"Bomba {estoque_item.bomba}"].append({
            'tipo': estoque_item.get_combustivel_display(),
            'quantidade_disponivel': float(estoque_item.quantidade_disponivel), # Converter para float para JS
            'capacidade_maxima': float(estoque_item.capacidade_maxima) if estoque_item.capacidade_maxima else 0.0
        })
    
    # Transforma o defaultdict de volta para a estrutura que o template espera
    # Esta estrutura será consumida pelo JavaScript
    bombas_para_js = [{'nome': bomba_nome, 'combustiveis': combustiveis_list}
                      for bomba_nome, combustiveis_list in bombas_info.items()]

    context = {
        'bombas': bombas_para_js # Passamos os dados brutos ou semi-brutos para o template
    }
    return render(request, 'index.html', context)

def venda(request):  # Esta é a função que você vai alterar
    bombas = Venda.BOMBA_CHOICES
    combustiveis = Venda.COMBUSTIVEL_CHOICES
    pagamentos = Venda.PAGAMENTO_CHOICES
    context = {
        'bombas': bombas,
        'combustiveis': combustiveis,
        'pagamentos': pagamentos,
    }
    return render(request, 'venda.html', context) # Agora renderiza com o CONTEXTO


def reabastecer(request):
    return render(request, 'reabastecer.html') # renderiza o template reabastecer


def relatorio(request):
    return render(request, 'relatorio.html') # renderiza o template relatorio


# View para exibir o formulário (se você ainda não tem)
def formulario_venda_view(request):
    # Você pode passar as choices para o template se precisar preencher os <select> dinamicamente
    bombas = Venda.BOMBA_CHOICES
    combustiveis = Venda.COMBUSTIVEL_CHOICES
    pagamentos = Venda.PAGAMENTO_CHOICES
    context = {
        'bombas': bombas,
        'combustiveis': combustiveis,
        'pagamentos': pagamentos,
    }
    return render(request, 'seu_template_do_formulario.html', context)


# gestaoPostoCombustivel/views.py

# ... (suas outras views: index, venda, reabastecer, relatorio - a view 'venda' já deve estar passando o contexto com BOMBA_CHOICES, etc.) ...

def registrar_venda_view(request):
    if request.method == 'POST':
        bomba_id = request.POST.get('bomba_selecionada')
        combustivel_tipo = request.POST.get('tipo_combustivel')
        quantidade_vendida_str = request.POST.get('quantidade_litros')
        forma_pagamento = request.POST.get('forma_pagamento')
        # NÃO pegamos mais o valor_total do formulário

        # Validação dos campos recebidos (exceto valor_total que será calculado)
        if not all([bomba_id, combustivel_tipo, quantidade_vendida_str, forma_pagamento]):
            messages.error(request, "Todos os campos obrigatórios (bomba, combustível, quantidade, pagamento) devem ser preenchidos!")
            return redirect('venda')

        try:
            quantidade_vendida = Decimal(quantidade_vendida_str)
            if quantidade_vendida <= 0: # Validação adicional para quantidade
                messages.error(request, "A quantidade vendida deve ser maior que zero.")
                return redirect('venda')
        except InvalidOperation:
            messages.error(request, "Quantidade inválida. Use um número válido.")
            return redirect('venda')

        try:
            with transaction.atomic():
                # PASSO NOVO: Buscar o preço do combustível
                try:
                    preco_obj = PrecoCombustivel.objects.get(combustivel=combustivel_tipo)
                    preco_unitario = preco_obj.preco_por_litro
                except PrecoCombustivel.DoesNotExist:
                    messages.error(request, f"O preço para o combustível '{combustivel_tipo}' não foi encontrado no sistema. Por favor, cadastre o preço primeiro.")
                    return redirect('venda')

                # PASSO NOVO: Calcular o valor total
                valor_total_calculado = preco_unitario * quantidade_vendida
                # Arredondar para 2 casas decimais, padrão para moeda
                valor_total_calculado = valor_total_calculado.quantize(Decimal('0.01'))

                # Continuar com a lógica de buscar estoque, etc.
                try:
                    estoque_da_bomba = Estoque.objects.get(bomba=bomba_id)
                except Estoque.DoesNotExist:
                    messages.error(request, f"Estoque para a Bomba {bomba_id} não encontrado.")
                    return redirect('venda')

                if estoque_da_bomba.combustivel != combustivel_tipo:
                    # Esta verificação pode ser opcional se uma bomba puder ter combustíveis variáveis
                    # e o estoque já reflete o combustível correto para aquela bomba.
                    # Mas se cada bomba SÓ TEM UM tipo de combustível, esta validação é boa.
                    messages.error(request, f"O combustível {combustivel_tipo} não corresponde ao combustível da Bomba {bomba_id} ({estoque_da_bomba.combustivel}).")
                    return redirect('venda')

                if estoque_da_bomba.quantidade_disponivel < quantidade_vendida:
                    messages.error(request, f"Estoque insuficiente de {estoque_da_bomba.get_combustivel_display()} na Bomba {bomba_id}. Disponível: {estoque_da_bomba.quantidade_disponivel}L.")
                    return redirect('venda')

                # Criar o registro de Venda com o valor_total_calculado
                nova_venda = Venda.objects.create(
                    bomba=bomba_id,
                    combustivel=combustivel_tipo,
                    quantidade=quantidade_vendida,
                    pagamento=forma_pagamento,
                    valor=valor_total_calculado # USANDO O VALOR CALCULADO AQUI
                )

                # Atualizar a quantidade_disponivel no Estoque
                estoque_da_bomba.quantidade_disponivel -= quantidade_vendida
                estoque_da_bomba.save()

                # Use get_combustivel_display() para mostrar o nome amigável do combustível na mensagem
                messages.success(request, f"Venda de {quantidade_vendida}L de {nova_venda.get_combustivel_display()} (R$ {valor_total_calculado}) registrada com sucesso! Estoque atualizado.")
                return redirect('venda')

        except Exception as e: # Captura outras exceções gerais
            messages.error(request, f"Ocorreu um erro inesperado ao processar a venda: {e}")
            return redirect('venda')
    else:
        # Se o método não for POST, redireciona para a página de venda
        return redirect('venda')
