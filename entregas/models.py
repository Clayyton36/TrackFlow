import secrets
import string

from django.conf import settings
from django.db import models


def gerar_codigo_rastreio() -> str:
    alfabeto = string.ascii_uppercase + string.digits
    sufixo = "".join(secrets.choice(alfabeto) for _ in range(6))
    return f"TRK-{sufixo}"


class Empresa(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="empresa")
    nome_fantasia = models.CharField(max_length=150)
    telefone = models.CharField(max_length=20, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome_fantasia


class Entrega(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="entregas")
    codigo_rastreio = models.CharField(max_length=20, unique=True, editable=False)

    cliente_nome = models.CharField(max_length=150)
    cliente_contato = models.CharField(max_length=100, blank=True)

    origem = models.CharField(max_length=200)
    destino = models.CharField(max_length=200)
    transportadora = models.CharField(max_length=100, blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]

    def save(self, *args, **kwargs):
        if not self.codigo_rastreio:
            codigo = gerar_codigo_rastreio()
            while Entrega.objects.filter(codigo_rastreio=codigo).exists():
                codigo = gerar_codigo_rastreio()
            self.codigo_rastreio = codigo
        super().save(*args, **kwargs)

    @property
    def status_atual(self) -> str | None:
        ultimo = self.historico.order_by("-data_hora").first()
        return ultimo.status if ultimo else None

    def __str__(self):
        return self.codigo_rastreio


def foto_upload_path(instance: "StatusHistorico", filename: str) -> str:
    return f"entregas/{instance.entrega.codigo_rastreio}/{instance.status}_{filename}"


class StatusHistorico(models.Model):
    AGENDADO = "AGENDADO"
    COLETADO = "COLETADO"
    EM_TRANSITO = "EM_TRANSITO"
    SAIU_PARA_ENTREGA = "SAIU_PARA_ENTREGA"
    ENTREGUE = "ENTREGUE"
    EXTRAVIADO = "EXTRAVIADO"

    STATUS_CHOICES = [
        (AGENDADO, "Agendado"),
        (COLETADO, "Coletado"),
        (EM_TRANSITO, "Em trânsito"),
        (SAIU_PARA_ENTREGA, "Saiu para entrega"),
        (ENTREGUE, "Entregue"),
        (EXTRAVIADO, "Extraviado"),
    ]

    # Estados a partir dos quais cada status pode ser alcançado.
    # None (chave ausente) = não pode ser o estado inicial de uma entrega nova.
    TRANSICOES_VALIDAS = {
        AGENDADO: [],  # só é válido como primeiro status de uma entrega
        COLETADO: [AGENDADO],
        EM_TRANSITO: [COLETADO],
        SAIU_PARA_ENTREGA: [EM_TRANSITO],
        ENTREGUE: [SAIU_PARA_ENTREGA],
        EXTRAVIADO: [COLETADO, EM_TRANSITO, SAIU_PARA_ENTREGA],
    }

    # Status em que a foto de comprovação é obrigatória.
    STATUS_COM_FOTO_OBRIGATORIA = {COLETADO, ENTREGUE}

    entrega = models.ForeignKey(Entrega, on_delete=models.CASCADE, related_name="historico")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    data_hora = models.DateTimeField(auto_now_add=True)
    observacao = models.CharField(max_length=255, blank=True)
    foto = models.ImageField(upload_to=foto_upload_path, blank=True, null=True)

    class Meta:
        ordering = ["data_hora"]
        verbose_name_plural = "Status históricos"

    def __str__(self):
        return f"{self.entrega.codigo_rastreio} → {self.status}"

    @staticmethod
    def transicao_valida(status_atual: str | None, novo_status: str) -> bool:
        """Verifica se `novo_status` pode suceder `status_atual` (None = entrega nova)."""
        if status_atual is None:
            return novo_status == StatusHistorico.AGENDADO
        origens_permitidas = StatusHistorico.TRANSICOES_VALIDAS.get(novo_status, [])
        return status_atual in origens_permitidas

    @staticmethod
    def foto_obrigatoria_para(status: str) -> bool:
        return status in StatusHistorico.STATUS_COM_FOTO_OBRIGATORIA
