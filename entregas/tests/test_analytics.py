from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from entregas.analytics import calcular_metricas, formatar_duracao
from entregas.models import StatusHistorico
from entregas.tests.factories import criar_empresa, criar_entrega


def registrar_status(entrega, status, quando=None):
    evento = StatusHistorico.objects.create(entrega=entrega, status=status)
    if quando is not None:
        StatusHistorico.objects.filter(pk=evento.pk).update(data_hora=quando)
    return evento


class FormatarDuracaoTests(TestCase):
    def test_none_retorna_travessao(self):
        self.assertEqual(formatar_duracao(None), "—")

    def test_menos_de_um_dia(self):
        self.assertEqual(formatar_duracao(timedelta(hours=5)), "5h")

    def test_dias_e_horas(self):
        self.assertEqual(formatar_duracao(timedelta(days=2, hours=3)), "2 dia(s) e 3h")

    def test_dias_exatos(self):
        self.assertEqual(formatar_duracao(timedelta(days=1)), "1 dia(s)")


class CalcularMetricasTests(TestCase):
    def setUp(self):
        self.empresa = criar_empresa()

    def test_sem_entregas(self):
        metricas = calcular_metricas(self.empresa)
        self.assertEqual(metricas["total_entregas"], 0)
        self.assertIsNone(metricas["tempo_medio_entrega"])
        self.assertEqual(metricas["atrasadas"], [])
        self.assertEqual(metricas["por_transportadora"], [])

    def test_tempo_medio_de_entrega(self):
        agora = timezone.now()
        entrega = criar_entrega(empresa=self.empresa, transportadora="Rápida")
        entrega.criado_em = agora - timedelta(days=2)
        entrega.save()
        registrar_status(entrega, StatusHistorico.AGENDADO, quando=agora - timedelta(days=2))
        registrar_status(entrega, StatusHistorico.ENTREGUE, quando=agora)

        metricas = calcular_metricas(self.empresa)

        self.assertEqual(metricas["entregues"], 1)
        self.assertEqual(metricas["tempo_medio_entrega"], timedelta(days=2))
        self.assertEqual(metricas["tempo_medio_entrega_formatado"], "2 dia(s)")

    def test_entrega_com_prazo_vencido_e_nao_entregue_conta_como_atrasada(self):
        entrega = criar_entrega(empresa=self.empresa, prazo_entrega=(timezone.now() - timedelta(days=1)).date())
        registrar_status(entrega, StatusHistorico.AGENDADO)

        metricas = calcular_metricas(self.empresa)

        self.assertEqual(metricas["atrasadas"], [entrega])

    def test_entrega_entregue_nao_conta_como_atrasada_mesmo_com_prazo_vencido(self):
        entrega = criar_entrega(empresa=self.empresa, prazo_entrega=(timezone.now() - timedelta(days=1)).date())
        registrar_status(entrega, StatusHistorico.AGENDADO)
        registrar_status(entrega, StatusHistorico.COLETADO)
        registrar_status(entrega, StatusHistorico.EM_TRANSITO)
        registrar_status(entrega, StatusHistorico.SAIU_PARA_ENTREGA)
        registrar_status(entrega, StatusHistorico.ENTREGUE)

        metricas = calcular_metricas(self.empresa)

        self.assertEqual(metricas["atrasadas"], [])

    def test_entrega_sem_prazo_nunca_e_atrasada(self):
        entrega = criar_entrega(empresa=self.empresa, prazo_entrega=None)
        registrar_status(entrega, StatusHistorico.AGENDADO)

        metricas = calcular_metricas(self.empresa)

        self.assertEqual(metricas["atrasadas"], [])

    def test_agrupamento_por_transportadora(self):
        criar_entrega(empresa=self.empresa, transportadora="Rápida")
        criar_entrega(empresa=self.empresa, transportadora="Rápida")
        criar_entrega(empresa=self.empresa, transportadora="Vagarosa")
        criar_entrega(empresa=self.empresa, transportadora="")

        metricas = calcular_metricas(self.empresa)
        por_nome = {item["nome"]: item for item in metricas["por_transportadora"]}

        self.assertEqual(por_nome["Rápida"]["quantidade"], 2)
        self.assertEqual(por_nome["Rápida"]["percentual_da_maior"], 100)
        self.assertEqual(por_nome["Vagarosa"]["quantidade"], 1)
        self.assertEqual(por_nome["Vagarosa"]["percentual_da_maior"], 50)
        self.assertEqual(por_nome["Não informada"]["quantidade"], 1)

    def test_metricas_sao_isoladas_por_empresa(self):
        outra_empresa = criar_empresa(username="outra-loja")
        criar_entrega(empresa=outra_empresa, transportadora="Concorrente")

        metricas = calcular_metricas(self.empresa)

        self.assertEqual(metricas["total_entregas"], 0)
