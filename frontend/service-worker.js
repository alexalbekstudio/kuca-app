const CACHE_NAME = 'kuca-app-v2';

self.addEventListener('install', (event) => {
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) => {
            return Promise.all(
                keys.map((key) => {
                    if (key !== CACHE_NAME) {
                        return caches.delete(key);
                    }
                })
            );
        })
    );
    self.clients.claim();
});

// NE presreći API pozive - pusti ih direktno na mrežu
self.addEventListener('fetch', (event) => {
    // Ako je API poziv, pusti ga direktno (nemoj keširati)
    if (event.request.url.includes('/api/')) {
        return;
    }

    // Za ostale fajlove (HTML, CSS, slike) koristi mrežu
    event.respondWith(
        fetch(event.request).catch(() => {
            return caches.match(event.request);
        })
    );
});