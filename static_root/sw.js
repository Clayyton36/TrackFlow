const CACHE_ESTATICOS = "trackflow-estaticos-v1";

const ARQUIVOS_APP_SHELL = [
    "/static/css/style.css",
    "/static/js/rastreio.js",
    "/static/icons/icon-192.png",
    "/static/icons/icon-512.png",
];

self.addEventListener("install", function (event) {
    event.waitUntil(
        caches.open(CACHE_ESTATICOS).then(function (cache) {
            return cache.addAll(ARQUIVOS_APP_SHELL);
        })
    );
    self.skipWaiting();
});

self.addEventListener("activate", function (event) {
    event.waitUntil(
        caches.keys().then(function (chaves) {
            return Promise.all(
                chaves
                    .filter(function (chave) {
                        return chave !== CACHE_ESTATICOS;
                    })
                    .map(function (chave) {
                        return caches.delete(chave);
                    })
            );
        })
    );
    self.clients.claim();
});

// Só arquivos estáticos usam cache-first. Páginas e a API de rastreio sempre
// vão direto pra rede — status de entrega não pode ficar desatualizado.
self.addEventListener("fetch", function (event) {
    const url = new URL(event.request.url);
    const eEstatico = url.pathname.startsWith("/static/");

    if (!eEstatico || event.request.method !== "GET") {
        return;
    }

    event.respondWith(
        caches.match(event.request).then(function (respostaCache) {
            return (
                respostaCache ||
                fetch(event.request).then(function (respostaRede) {
                    return caches.open(CACHE_ESTATICOS).then(function (cache) {
                        cache.put(event.request, respostaRede.clone());
                        return respostaRede;
                    });
                })
            );
        })
    );
});
