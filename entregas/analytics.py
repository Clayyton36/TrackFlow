from datetime import timedelta

from django.utils import timezone

from .models import Empresa, StatusHistorico


def formatar_duracao(delta: timedelta | None) -> str:
    if delta is None:
        return "—"
    total_horas = int(delta.total_seconds() // 3600)
    dias, horas = divmod(total_horas, 24)
    if dias and horas:
        return f"{dias} dia(s) e {horas}h"
    if dias:
        return f"{dias} dia(s)"
    return f"{horas}h"


def calcular_metricas(empresa: Empresa) -> dict:
    entregas = list(empresa.entregas.prefetch_related("historico"))
    hoje = timezone.localdate()

    tempos_entrega = []
    atrasadas = []
    contagem_por_transportadora: dict[str, int] = {}
    entregues = 0

    for entrega in entregas:
        historico = list(entrega.historico.all())
        status_atual = historico[-1].status if historico else None

        transportadora = entrega.transportadora or "Não informada"
        contagem_por_transportadora[transportadora] = contagem_por_transportadora.get(transportadora, 0) + 1

        if status_atual == StatusHistorico.ENTREGUE:
            entregues += 1
            evento_entrega = next(e for e in historico if e.status == StatusHistorico.ENTREGUE)
            tempos_entrega.append(evento_entrega.data_hora - entrega.criado_em)

        if entrega.prazo_entrega and entrega.prazo_entrega < hoje and status_atual != StatusHistorico.ENTREGUE:
            atrasadas.append(entrega)

    tempo_medio_entrega = (
        sum(tempos_entrega, timedelta()) / len(tempos_entrega) if tempos_entrega else None
    )

    maior_contagem = max(contagem_por_transportadora.values(), default=0)
    por_transportadora = [
        {
            "nome": nome,
            "quantidade": quantidade,
            "percentual_da_maior": round(quantidade / maior_contagem * 100) if maior_contagem else 0,
        }
        for nome, quantidade in sorted(contagem_por_transportadora.items(), key=lambda item: -item[1])
    ]

    return {
        "total_entregas": len(entregas),
        "entregues": entregues,
        "tempo_medio_entrega": tempo_medio_entrega,
        "tempo_medio_entrega_formatado": formatar_duracao(tempo_medio_entrega),
        "atrasadas": atrasadas,
        "por_transportadora": por_transportadora,
    }
