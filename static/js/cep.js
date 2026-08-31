(function () {
    "use strict";

    var CEP_VALIDO = /^\d{8}$/;

    function formatarEndereco(dados) {
        var partes = [dados.logradouro, dados.bairro, dados.localidade + " - " + dados.uf].filter(function (parte) {
            return Boolean(parte);
        });
        return partes.join(", ");
    }

    function buscarCep(cepBruto) {
        var cep = cepBruto.replace(/\D/g, "");
        if (!CEP_VALIDO.test(cep)) {
            return Promise.reject(new Error("CEP precisa ter 8 dígitos."));
        }
        return fetch("https://viacep.com.br/ws/" + cep + "/json/").then(function (resposta) {
            if (!resposta.ok) {
                throw new Error("Erro ao consultar o CEP.");
            }
            return resposta.json();
        }).then(function (dados) {
            if (dados.erro) {
                throw new Error("CEP não encontrado.");
            }
            return dados;
        });
    }

    function ligarAutocompleteCep(idCep, idEndereco, idStatus) {
        var inputCep = document.getElementById(idCep);
        var inputEndereco = document.getElementById(idEndereco);
        var status = document.getElementById(idStatus);
        if (!inputCep || !inputEndereco || !status) return;

        inputCep.addEventListener("blur", function () {
            var valor = inputCep.value.trim();
            if (!valor) {
                status.textContent = "";
                return;
            }
            status.textContent = "Buscando endereço...";
            buscarCep(valor).then(function (dados) {
                inputEndereco.value = formatarEndereco(dados);
                status.textContent = "Endereço preenchido — confira o número.";
            }).catch(function (erro) {
                status.textContent = erro.message;
            });
        });
    }

    document.addEventListener("DOMContentLoaded", function () {
        ligarAutocompleteCep("cep-origem", "id_origem", "status-cep-origem");
        ligarAutocompleteCep("cep-destino", "id_destino", "status-cep-destino");
    });
})();
