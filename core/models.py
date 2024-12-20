from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta

class Farmacia(AbstractUser):
    nome_loja = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14, null=True, blank=True, help_text="Digite o CPF no formato: 000.000.000-00")
    email = models.EmailField(null=True, blank=True)
    
    def __str__(self):
        return self.nome_loja

    class Meta:
        verbose_name = "Farmácia"
        verbose_name_plural = "Farmácias"

class Produto(models.Model):
    CATEGORIA_CHOICES = [
        ('MEDICAMENTO', 'Medicamento'),
        ('CONTROLADO', 'Controlado'),
        ('TERMOLABEL', 'Termolábel'),
        ('ALIMENTO', 'Alimento'),
        ('PERFUMARIA', 'Perfumaria'),
    ]
    
    STATUS_CHOICES = [
        ('ATIVO', 'Ativo'),
        ('RETIRADO', 'Retirado'),
    ]

    farmacia = models.ForeignKey(Farmacia, on_delete=models.CASCADE)
    codigo_barras = models.CharField(max_length=13)
    descricao = models.CharField(max_length=200)
    categoria = models.CharField(
        max_length=20,
        choices=CATEGORIA_CHOICES,
        default='MEDICAMENTO'
    )
    data_validade = models.DateField()
    quantidade = models.IntegerField()
    lote = models.CharField(max_length=50)
    data_cadastro = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ATIVO')
    data_retirada = models.DateTimeField(null=True, blank=True)
    motivo_retirada = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-data_cadastro']

    def __str__(self):
        return f"{self.descricao} - Lote: {self.lote}"

    @property
    def status_validade(self):
        dias_para_vencer = (self.data_validade - timezone.now().date()).days
        if dias_para_vencer <= 15:
            return 'danger'  # Vermelho
        elif dias_para_vencer <= 90:
            return 'warning'  # Amarelo
        return 'normal'  # Sem destaque

    @property
    def dias_para_vencer(self):
        return (self.data_validade - timezone.now().date()).days
