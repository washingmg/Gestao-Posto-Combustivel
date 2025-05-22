from django.shortcuts import render

# cada view vai ser uma função (no momento) que vai dizer o que vai ser feita, quando a requisição for feita
def index(request):
    return render(request, 'index.html') # renderiza o template indexhtml

def venda(request):
    return render(request, 'venda.html') # renderiza o template venda

def reabastecer(request):
    return render(request, 'reabastecer.html') # renderiza o template reabastecer

def relatorio(request):
    return render(request, 'relatorio.html') # renderiza o template relatorio