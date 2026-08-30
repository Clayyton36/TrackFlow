(function () {
    "use strict";

    var STATUS_FINAIS = ["ENTREGUE", "EXTRAVIADO"];
    var INTERVALO_POLLING_MS = 30000;

    var form = document.getElementById("form-busca");
    var input = document.getElementById("codigo-rastreio");
    var resultado = document.getElementById("resultado");
    var mensagemStatus = document.getElementById("mensagem-status");
    var timerPolling = null;

    function limparResultado() {
        while (resultado.firstChild) {
            resultado.removeChild(resultado.firstChild);
        }
    }

    function criarElemento(tag, opcoes) {
        var el = document.createElement(tag);
        opcoes = opcoes || {};
        if (opcoes.texto) el.textContent = opcoes.texto;
        if (opcoes.classe) el.className = opcoes.classe;
        return el;
    }

    function renderizarEntrega(dados) {
        limparResultado();

        var titulo = criarElemento("h2", { texto: "Entrega " + dados.codigo_rastreio });
        resultado.appendChild(titulo);

        var info = criarElemento("p", {
            texto: "Cliente: " + dados.cliente_nome + " — " + dados.origem + " → " + dados.destino,
        });
        resultado.appendChild(info);

        if (dados.transportadora) {
            resultado.appendChild(
                criarElemento("p", { texto: "Transportadora: " + dados.transportadora })
            );
        }

        var lista = criarElemento("ol", { classe: "timeline" });
        dados.historico.forEach(function (evento) {
            var item = criarElemento("li", {
                classe: "status-" + evento.status.toLowerCase(),
            });

            item.appendChild(criarElemento("span", { classe: "status-nome", texto: evento.status_display }));
            item.appendChild(document.createTextNode(" "));
            item.appendChild(
                criarElemento("span", { classe: "status-data", texto: formatarData(evento.data_hora) })
            );

            if (evento.observacao) {
                item.appendChild(criarElemento("p", { texto: evento.observacao }));
            }

            if (evento.foto_url) {
                var img = document.createElement("img");
                img.src = evento.foto_url;
                img.alt = "Foto de comprovação do status " + evento.status_display;
                item.appendChild(img);
            }

            lista.appendChild(item);
        });
        resultado.appendChild(lista);

        mensagemStatus.textContent = "Status atual: " + (dados.status_atual || "sem status");

        if (STATUS_FINAIS.indexOf(dados.status_atual) === -1) {
            agendarProximaAtualizacao(dados.codigo_rastreio);
        } else if (timerPolling) {
            clearTimeout(timerPolling);
        }
    }

    function formatarData(isoString) {
        var data = new Date(isoString);
        return data.toLocaleString("pt-BR");
    }

    function agendarProximaAtualizacao(codigo) {
        if (timerPolling) clearTimeout(timerPolling);
        timerPolling = setTimeout(function () {
            buscarEntrega(codigo, true);
        }, INTERVALO_POLLING_MS);
    }

    function buscarEntrega(codigo, silencioso) {
        if (!silencioso) {
            limparResultado();
            mensagemStatus.textContent = "Buscando...";
        }

        fetch("/api/rastreio/" + encodeURIComponent(codigo) + "/")
            .then(function (resposta) {
                if (!resposta.ok) {
                    throw new Error(resposta.status === 404 ? "Código não encontrado." : "Erro ao buscar entrega.");
                }
                return resposta.json();
            })
            .then(renderizarEntrega)
            .catch(function (erro) {
                if (timerPolling) clearTimeout(timerPolling);
                limparResultado();
                mensagemStatus.textContent = erro.message;
            });
    }

    form.addEventListener("submit", function (event) {
        event.preventDefault();
        var codigo = input.value.trim();
        if (codigo) {
            history.replaceState(null, "", "/rastreio/" + encodeURIComponent(codigo) + "/");
            buscarEntrega(codigo, false);
        }
    });

    if (input.value.trim()) {
        buscarEntrega(input.value.trim(), false);
    }
})();
