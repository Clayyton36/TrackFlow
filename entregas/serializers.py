from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .models import Entrega, StatusHistorico


class StatusHistoricoPublicoSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    foto_url = serializers.SerializerMethodField()

    class Meta:
        model = StatusHistorico
        fields = ["status", "status_display", "data_hora", "observacao", "foto_url"]

    @extend_schema_field(serializers.URLField(allow_null=True))
    def get_foto_url(self, obj):
        if not obj.foto:
            return None
        request = self.context.get("request")
        url = obj.foto.url
        return request.build_absolute_uri(url) if request else url


class EntregaPublicaSerializer(serializers.ModelSerializer):
    """Serializer exposto no endpoint público de rastreio.

    Deliberadamente NÃO inclui `empresa`, `cliente_contato` ou qualquer
    outro dado interno/sensível — só o necessário para o cliente acompanhar
    a entrega.
    """

    status_atual = serializers.CharField(read_only=True)
    historico = StatusHistoricoPublicoSerializer(many=True, read_only=True)

    class Meta:
        model = Entrega
        fields = [
            "codigo_rastreio",
            "origem",
            "destino",
            "transportadora",
            "cliente_nome",
            "status_atual",
            "historico",
        ]
