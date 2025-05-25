# gestaoPostoCombustivel/models.py
from django.db import models

# Constantes de CHOICES (opções para campos)
BOMBA_IDENTIFICADORES = [
    ('A', 'Bomba A'), ('B', 'Bomba B'),
    ('C', 'Bomba C'), ('D', 'Bomba D'),
]
TIPO_COMBUSTIVEL_CHOICES = [
    ('etanol', 'Etanol'),
    ('diesel_comum', 'Diesel'), # Diesel Comum
    ('gasolina_comum', 'Gasolina Comum'), # Gasolina Comum
    ('gasolina_aditivada', 'Gasolina Aditivada'),
    ('diesel_s10', 'Diesel S10'), # Exemplo de outro tipo
    # Adicione outros tipos conforme sua necessidade
]
PAGAMENTO_CHOICES = [
    ('credito', 'Cartão de Crédito'),
    ('debito', 'Cartão de Débito'),
    ('dinheiro', 'Dinheiro'),
    ('pix', 'Pix'),
]

class PrecoCombustivel(models.Model):
    """
    Representa um tipo de combustível e seu preço por litro.
    """
    id_combustivel = models.CharField(
        max_length=20,
        choices=TIPO_COMBUSTIVEL_CHOICES, # Os valores aqui ('etanol', 'gasolina') serão as chaves
        unique=True,
        primary_key=True
    )
    preco_por_litro = models.DecimalField(max_digits=6, decimal_places=2)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_id_combustivel_display()} - R$ {self.preco_por_litro}/L"

    class Meta:
        verbose_name = "Combustível (Preço)"
        verbose_name_plural = "Combustíveis (Preços)"


class Bomba(models.Model):
    """
    Representa uma bomba física no posto.
    """
    id_bomba = models.CharField(
        max_length=1,
        choices=BOMBA_IDENTIFICADORES,
        unique=True,
        primary_key=True
    )
    # Define quais combustíveis esta bomba específica pode dispensar.
    combustiveis_disponiveis = models.ManyToManyField(
        PrecoCombustivel,
        related_name='bombas_que_dispensam'
    )
    # Ex: localizacao = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.get_id_bomba_display()


class Tanque(models.Model):
    """
    Representa um tanque de armazenamento para um tipo específico de combustível.
    Este modelo substitui o antigo 'Estoque'.
    """
    # Cada tipo de combustível tem seu próprio tanque principal de armazenamento.
    combustivel = models.OneToOneField(
        PrecoCombustivel,
        on_delete=models.PROTECT, # Não permite deletar um tipo de combustível se ele tem um tanque.
        primary_key=True
    )
    quantidade_disponivel = models.DecimalField(max_digits=10, decimal_places=2)
    capacidade_maxima = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        base_str = f"Tanque de {self.combustivel.get_id_combustivel_display()}: {self.quantidade_disponivel}L"
        if self.capacidade_maxima and self.capacidade_maxima > 0:
            base_str += f" de {self.capacidade_maxima}L"
            percentual = (self.quantidade_disponivel / self.capacidade_maxima) * 100
            base_str += f" ({percentual:.1f}%)"
        return base_str

    class Meta:
        verbose_name = "Tanque de Combustível"
        verbose_name_plural = "Tanques de Combustíveis"


class Venda(models.Model):
    """
    Registra uma venda de combustível.
    """
    bomba = models.ForeignKey(Bomba, on_delete=models.PROTECT)
    combustivel = models.ForeignKey(PrecoCombustivel, on_delete=models.PROTECT) # O tipo de combustível vendido
    quantidade = models.DecimalField(max_digits=10, decimal_places=2)
    pagamento = models.CharField(max_length=10, choices=PAGAMENTO_CHOICES)
    valor = models.DecimalField(max_digits=10, decimal_places=2) # Será calculado na view
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (f"Venda ({self.id}): Bomba {self.bomba.id_bomba} - "
                f"{self.combustivel.get_id_combustivel_display()} - {self.quantidade}L - R${self.valor} - "
                f"{self.data.strftime('%d/%m/%Y %H:%M')}")

# Modelo para Reabastecimentos (sugestão para o futuro, pode adicionar depois)
# class ReabastecimentoTanque(models.Model):
#     tanque = models.ForeignKey(Tanque, on_delete=models.CASCADE)
#     quantidade_adicionada = models.DecimalField(max_digits=10, decimal_places=2)
#     data_reabastecimento = models.DateTimeField(auto_now_add=True)
#     # ... outros campos como fornecedor, nota_fiscal, etc.
#
#     def __str__(self):
#         return f"Reabastecimento {self.tanque.combustivel.get_id_combustivel_display()} - {self.quantidade_adicionada}L em {self.data_reabastecimento.strftime('%d/%m/%Y')}"