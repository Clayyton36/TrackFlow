from django.test import TestCase

from entregas.forms import StatusHistoricoForm
from entregas.models import StatusHistorico
from entregas.tests.factories import criar_entrega, imagem_falsa


class StatusHistoricoFormTests(TestCase):
    def test_agendado_sem_foto_e_valido(self):
        entrega = criar_entrega()
        form = StatusHistoricoForm(
            data={"status": StatusHistorico.AGENDADO, "observacao": ""}, entrega=entrega
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_coletado_sem_foto_e_invalido(self):
        entrega = criar_entrega()
        StatusHistorico.objects.create(entrega=entrega, status=StatusHistorico.AGENDADO)

        form = StatusHistoricoForm(
            data={"status": StatusHistorico.COLETADO, "observacao": ""}, entrega=entrega
        )

        self.assertFalse(form.is_valid())
        self.assertIn("foto", str(form.errors))

    def test_coletado_com_foto_e_valido(self):
        entrega = criar_entrega()
        StatusHistorico.objects.create(entrega=entrega, status=StatusHistorico.AGENDADO)

        form = StatusHistoricoForm(
            data={"status": StatusHistorico.COLETADO, "observacao": ""},
            files={"foto": imagem_falsa()},
            entrega=entrega,
        )

        self.assertTrue(form.is_valid(), form.errors)

    def test_nao_oferece_transicao_invalida_como_opcao(self):
        entrega = criar_entrega()
        StatusHistorico.objects.create(entrega=entrega, status=StatusHistorico.AGENDADO)

        form = StatusHistoricoForm(entrega=entrega)

        valores_disponiveis = [valor for valor, _ in form.fields["status"].choices]
        self.assertNotIn(StatusHistorico.ENTREGUE, valores_disponiveis)
        self.assertIn(StatusHistorico.COLETADO, valores_disponiveis)

    def test_entrega_sem_status_so_oferece_agendado(self):
        entrega = criar_entrega()
        form = StatusHistoricoForm(entrega=entrega)
        valores_disponiveis = [valor for valor, _ in form.fields["status"].choices]
        self.assertEqual(valores_disponiveis, [StatusHistorico.AGENDADO])
