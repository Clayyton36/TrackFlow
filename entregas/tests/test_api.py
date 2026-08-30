from rest_framework.test import APITestCase

from entregas.models import StatusHistorico
from entregas.tests.factories import criar_entrega, imagem_falsa


class RastreioPublicoAPITests(APITestCase):
    def test_rastreio_existente_retorna_dados(self):
        entrega = criar_entrega()
        StatusHistorico.objects.create(entrega=entrega, status=StatusHistorico.AGENDADO)

        resposta = self.client.get(f"/api/rastreio/{entrega.codigo_rastreio}/")

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.data["codigo_rastreio"], entrega.codigo_rastreio)
        self.assertEqual(resposta.data["status_atual"], StatusHistorico.AGENDADO)
        self.assertEqual(len(resposta.data["historico"]), 1)

    def test_rastreio_inexistente_retorna_404(self):
        resposta = self.client.get("/api/rastreio/TRK-INEXISTENTE/")
        self.assertEqual(resposta.status_code, 404)

    def test_api_publica_nao_expoe_dados_sensiveis(self):
        entrega = criar_entrega(cliente_contato="11999999999")

        resposta = self.client.get(f"/api/rastreio/{entrega.codigo_rastreio}/")

        self.assertNotIn("empresa", resposta.data)
        self.assertNotIn("cliente_contato", resposta.data)

    def test_foto_de_status_aparece_como_url_no_historico(self):
        entrega = criar_entrega()
        StatusHistorico.objects.create(
            entrega=entrega, status=StatusHistorico.AGENDADO
        )
        StatusHistorico.objects.create(
            entrega=entrega, status=StatusHistorico.COLETADO, foto=imagem_falsa()
        )

        resposta = self.client.get(f"/api/rastreio/{entrega.codigo_rastreio}/")

        evento_coletado = resposta.data["historico"][1]
        self.assertIsNotNone(evento_coletado["foto_url"])

    def test_evento_sem_foto_retorna_foto_url_nula(self):
        entrega = criar_entrega()
        StatusHistorico.objects.create(entrega=entrega, status=StatusHistorico.AGENDADO)

        resposta = self.client.get(f"/api/rastreio/{entrega.codigo_rastreio}/")

        self.assertIsNone(resposta.data["historico"][0]["foto_url"])
