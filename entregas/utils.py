import io

from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image, ImageOps

LARGURA_MAXIMA = 1280


def processar_foto(arquivo) -> InMemoryUploadedFile:
    """Remove metadados EXIF (pode conter GPS de onde a foto foi tirada) e
    redimensiona para no máximo LARGURA_MAXIMA px, economizando espaço de storage.
    """
    imagem = Image.open(arquivo)
    imagem = ImageOps.exif_transpose(imagem)  # aplica rotação antes de descartar o EXIF
    imagem = imagem.convert("RGB")

    if imagem.width > LARGURA_MAXIMA:
        nova_altura = int(imagem.height * (LARGURA_MAXIMA / imagem.width))
        imagem = imagem.resize((LARGURA_MAXIMA, nova_altura), Image.LANCZOS)

    buffer = io.BytesIO()
    imagem.save(buffer, format="JPEG", quality=85)
    buffer.seek(0)

    nome = arquivo.name.rsplit(".", 1)[0] + ".jpg"
    return InMemoryUploadedFile(
        buffer, "ImageField", nome, "image/jpeg", buffer.getbuffer().nbytes, None
    )
