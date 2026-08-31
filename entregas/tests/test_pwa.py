import json

from django.conf import settings
from django.test import TestCase


class PWATests(TestCase):
    def test_service_worker_disponivel_na_raiz(self):
        # sw.js é servido via WHITENOISE_ROOT, direto do disco, então funciona
        # no test client mesmo sem collectstatic ter rodado.
        resposta = self.client.get("/sw.js")
        self.assertEqual(resposta.status_code, 200)
        self.assertIn("javascript", resposta["Content-Type"])

    def test_manifest_e_valido(self):
        # manifest.json vive em STATICFILES_DIRS/STATIC_ROOT, que só é servido
        # via HTTP depois de collectstatic — validamos o conteúdo direto do
        # arquivo fonte (a URL em si já foi conferida manualmente em dev/prod).
        caminho = settings.BASE_DIR / "static" / "manifest.json"
        dados = json.loads(caminho.read_text())

        self.assertEqual(dados["name"], "TrackFlow")
        self.assertEqual(dados["display"], "standalone")
        self.assertGreaterEqual(len(dados["icons"]), 2)

    def test_pagina_referencia_manifest_e_theme_color(self):
        resposta = self.client.get("/rastreio/")
        conteudo = resposta.content.decode()
        self.assertIn('rel="manifest"', conteudo)
        self.assertIn('name="theme-color"', conteudo)
