from django.db import models

class Venda(models.Model):
    BOMBA_CHOICES = [
        ('A', 'Bomba A'),
        ('B', 'Bomba B'),
        ('C', 'Bomba C'),
        ('D', 'Bomba D'),
    ]

    COMBUSTIVEL_CHOICES = [
        ('etanol', 'Etanol'),
        ('diesel', 'Diesel'),
        ('gasolina', 'Gasolina'),
        ('gasolina_aditivada', 'Gasolina Aditivada'),
    ]

    PAGAMENTO_CHOICES = [
        ('credito', 'Cartão de Crédito'),
        ('debito', 'Cartão de Débito'),
        ('dinheiro', 'Dinheiro'),
        ('pix', 'Pix'),
    ]

    bomba = models.CharField(max_length=1, choices=BOMBA_CHOICES)
    combustivel = models.CharField(max_length=20, choices=COMBUSTIVEL_CHOICES)
    quantidade = models.DecimalField(max_digits=10, decimal_places=2)
    pagamento = models.CharField(max_length=10, choices=PAGAMENTO_CHOICES)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.combustivel} - {self.quantidade}L - R${self.valor} - {self.data.strftime('%d/%m/%Y')}"


class Estoque(models.Model):
    bomba = models.CharField(max_length=1, unique=True, choices=Venda.BOMBA_CHOICES)
    combustivel = models.CharField(max_length=20, choices=Venda.COMBUSTIVEL_CHOICES)
    quantidade_disponivel = models.DecimalField(max_digits=10, decimal_places=2)
    capacidade_maxima = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    null=True,  # Permite nulo por agora, para facilitar a migração
    blank=True  # Permite campo em branco no admin por agora
)
   # Dentro da classe Estoque, no arquivo models.py

    def __str__(self):
        base_str = f"Bomba {self.bomba} - {self.get_combustivel_display()} - {self.quantidade_disponivel}L disponíveis"
        if self.capacidade_maxima: # Verifica se capacidade_maxima não é None
            base_str += f" (Cap: {self.capacidade_maxima}L)"
            if self.capacidade_maxima > 0: # Evita divisão por zero
                percentual = (self.quantidade_disponivel / self.capacidade_maxima) * 100
                base_str += f" ({percentual:.1f}%)"
        return base_str
# ... (seus modelos Venda e Estoque existentes) ...

class PrecoCombustivel(models.Model):
    # Usamos os mesmos COMBUSTIVEL_CHOICES do modelo Venda para consistência
    combustivel = models.CharField(
        max_length=20,
        choices=Venda.COMBUSTIVEL_CHOICES,
        unique=True,  # Garante que cada tipo de combustível só tenha um preço
        primary_key=True # Faz do campo 'combustivel' a chave primária
    )
    preco_por_litro = models.DecimalField(
        max_digits=6,   # Ex: 9999.99 (suficiente para preços por litro)
        decimal_places=2 # Duas casas decimais para o preço
    )
    data_atualizacao = models.DateTimeField(auto_now=True) # Para saber quando o preço foi atualizado

    def __str__(self):
        # get_combustivel_display() mostra o nome legível do combustível (ex: "Gasolina")
        return f"{self.get_combustivel_display()} - R$ {self.preco_por_litro}/L"

    class Meta:
        verbose_name = "Preço de Combustível"
        verbose_name_plural = "Preços de Combustíveis"