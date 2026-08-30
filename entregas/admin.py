from django.contrib import admin

from .models import Empresa, Entrega, StatusHistorico


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ["nome_fantasia", "usuario", "telefone"]


class StatusHistoricoInline(admin.TabularInline):
    model = StatusHistorico
    extra = 0
    readonly_fields = ["data_hora"]


@admin.register(Entrega)
class EntregaAdmin(admin.ModelAdmin):
    list_display = ["codigo_rastreio", "empresa", "cliente_nome", "status_atual", "criado_em"]
    inlines = [StatusHistoricoInline]
    readonly_fields = ["codigo_rastreio"]
