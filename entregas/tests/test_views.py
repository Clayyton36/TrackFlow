from django.test import TestCase

from entregas.tests.factories import criar_empresa


class CriarEntregaViewTests(TestCase):
    def setUp(self):
        self.empresa = criar_empresa()
        self.client.force_login(self.empresa.usuario)

    def test_pagina_tem_campos_de_cep_e_script_viacep(self):
        resposta = self.client.get("/entregas/nova/")
        conteudo = resposta.content.decode()

        self.assertEqual(resposta.status_code, 200)
        self.assertIn('id="cep-origem"', conteudo)
        self.assertIn('id="cep-destino"', conteudo)
        self.assertIn('id="status-cep-origem"', conteudo)
        self.assertIn('id="status-cep-destino"', conteudo)
        self.assertIn("js/cep", conteudo)

    def test_pagina_exige_login(self):
        self.client.logout()
        resposta = self.client.get("/entregas/nova/")
        self.assertEqual(resposta.status_code, 302)
