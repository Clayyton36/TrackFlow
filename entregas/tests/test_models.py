from django.db import IntegrityError
from django.test import TestCase

from entregas.models import StatusHistorico
from entregas.tests.factories import criar_entrega


class EntregaModelTests(TestCase):
    def test_codigo_rastreio_e_gerado_automaticamente(self):
        entrega = criar_entrega()
        self.assertTrue(entrega.codigo_rastreio.startswith("TRK-"))

    def test_codigo_rastreio_precisa_ser_unico(self):
        entrega = criar_entrega()
        outra = criar_entrega(empresa=entrega.empresa)
        outra.codigo_rastreio = entrega.codigo_rastreio
        with self.assertRaises(IntegrityError):
            outra.save()

    def test_status_atual_e_none_sem_historico(self):
        entrega = criar_entrega()
        self.assertIsNone(entrega.status_atual)

    def test_status_atual_reflete_ultimo_evento(self):
        entrega = criar_entrega()
        StatusHistorico.objects.create(entrega=entrega, status=StatusHistorico.AGENDADO)
        StatusHistorico.objects.create(entrega=entrega, status=StatusHistorico.COLETADO)
        self.assertEqual(entrega.status_atual, StatusHistorico.COLETADO)


class TransicaoStatusTests(TestCase):
    def test_agendado_e_valido_como_primeiro_status(self):
        self.assertTrue(StatusHistorico.transicao_valida(None, StatusHistorico.AGENDADO))

    def test_coletado_nao_pode_ser_o_primeiro_status(self):
        self.assertFalse(StatusHistorico.transicao_valida(None, StatusHistorico.COLETADO))

    def test_transicao_sequencial_valida(self):
        self.assertTrue(
            StatusHistorico.transicao_valida(StatusHistorico.AGENDADO, StatusHistorico.COLETADO)
        )
        self.assertTrue(
            StatusHistorico.transicao_valida(StatusHistorico.EM_TRANSITO, StatusHistorico.SAIU_PARA_ENTREGA)
        )

    def test_nao_pode_voltar_de_entregue_para_agendado(self):
        self.assertFalse(
            StatusHistorico.transicao_valida(StatusHistorico.ENTREGUE, StatusHistorico.AGENDADO)
        )

    def test_nao_pode_pular_etapas(self):
        self.assertFalse(
            StatusHistorico.transicao_valida(StatusHistorico.AGENDADO, StatusHistorico.ENTREGUE)
        )

    def test_extraviado_permitido_a_partir_de_em_transito(self):
        self.assertTrue(
            StatusHistorico.transicao_valida(StatusHistorico.EM_TRANSITO, StatusHistorico.EXTRAVIADO)
        )

    def test_foto_obrigatoria_para_coletado_e_entregue(self):
        self.assertTrue(StatusHistorico.foto_obrigatoria_para(StatusHistorico.COLETADO))
        self.assertTrue(StatusHistorico.foto_obrigatoria_para(StatusHistorico.ENTREGUE))
        self.assertFalse(StatusHistorico.foto_obrigatoria_para(StatusHistorico.EM_TRANSITO))
