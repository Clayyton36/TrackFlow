import io

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from entregas.models import Empresa, Entrega


def criar_empresa(username="loja", **kwargs):
    usuario = User.objects.create_user(username=username, password="senha-teste-123")
    return Empresa.objects.create(usuario=usuario, nome_fantasia=kwargs.pop("nome_fantasia", "Loja Teste"), **kwargs)


def criar_entrega(empresa=None, **kwargs):
    empresa = empresa or criar_empresa()
    dados = {
        "cliente_nome": "Cliente Teste",
        "cliente_contato": "cliente@example.com",
        "origem": "São Paulo, SP",
        "destino": "Campinas, SP",
        "transportadora": "Transportadora X",
    }
    dados.update(kwargs)
    return Entrega.objects.create(empresa=empresa, **dados)


def imagem_falsa(nome="foto.jpg"):
    buffer = io.BytesIO()
    Image.new("RGB", (10, 10), color="red").save(buffer, format="JPEG")
    buffer.seek(0)
    return SimpleUploadedFile(nome, buffer.read(), content_type="image/jpeg")
