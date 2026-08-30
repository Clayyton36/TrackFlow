from rest_framework.test import APITestCase


class DocumentacaoAPITests(APITestCase):
    def test_schema_openapi_disponivel(self):
        resposta = self.client.get("/api/schema/")
        self.assertEqual(resposta.status_code, 200)

    def test_swagger_ui_disponivel(self):
        resposta = self.client.get("/api/docs/")
        self.assertEqual(resposta.status_code, 200)
