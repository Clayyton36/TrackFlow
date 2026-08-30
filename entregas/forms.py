from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Empresa, Entrega, StatusHistorico
from .utils import processar_foto


class CadastroEmpresaForm(UserCreationForm):
    nome_fantasia = forms.CharField(max_length=150, label="Nome da empresa")
    telefone = forms.CharField(max_length=20, required=False, label="Telefone")

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def save(self, commit=True):
        usuario = super().save(commit=commit)
        Empresa.objects.create(
            usuario=usuario,
            nome_fantasia=self.cleaned_data["nome_fantasia"],
            telefone=self.cleaned_data["telefone"],
        )
        return usuario


class EntregaForm(forms.ModelForm):
    class Meta:
        model = Entrega
        fields = ["cliente_nome", "cliente_contato", "origem", "destino", "transportadora"]
        labels = {
            "cliente_nome": "Nome do cliente",
            "cliente_contato": "Contato do cliente (telefone/e-mail)",
            "origem": "Origem",
            "destino": "Destino",
            "transportadora": "Transportadora",
        }


class StatusHistoricoForm(forms.ModelForm):
    foto = forms.ImageField(
        required=False,
        label="Foto de comprovação",
        widget=forms.ClearableFileInput(attrs={"accept": "image/*", "capture": "environment"}),
    )

    class Meta:
        model = StatusHistorico
        fields = ["status", "observacao", "foto"]
        labels = {"status": "Novo status", "observacao": "Observação (opcional)"}

    def __init__(self, *args, entrega: Entrega, **kwargs):
        self.entrega = entrega
        super().__init__(*args, **kwargs)
        status_atual = entrega.status_atual
        opcoes_validas = [
            (valor, rotulo)
            for valor, rotulo in StatusHistorico.STATUS_CHOICES
            if StatusHistorico.transicao_valida(status_atual, valor)
        ]
        self.fields["status"].choices = opcoes_validas

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get("status")
        foto = cleaned_data.get("foto")

        if status and not StatusHistorico.transicao_valida(self.entrega.status_atual, status):
            raise forms.ValidationError(
                f"Não é possível mudar de '{self.entrega.status_atual}' para '{status}'."
            )

        if status and StatusHistorico.foto_obrigatoria_para(status) and not foto:
            raise forms.ValidationError(
                "É obrigatório anexar uma foto de comprovação para este status."
            )

        if foto:
            cleaned_data["foto"] = processar_foto(foto)

        return cleaned_data
