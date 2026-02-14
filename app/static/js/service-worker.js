const CACHE_NAME = 'habit-tracker-v1';
const ASSETS_TO_CACHE = [
    '/',
    '/static/css/base.css',
    '/static/css/themes.css',
    '/static/css/animations.css',
    '/static/js/app.js',
    '/static/js/api.js',
    '/static/js/calendar.js',
    '/static/js/habits.js',
    '/static/js/settings.js',
    '/static/js/themes.js',
    '/static/js/animations.js',
    '/static/img/favicon.svg',
    'https://unpkg.com/lucide@latest',
    'https://cdn.jsdelivr.net/npm/sortablejs@1.15.0/Sortable.min.js',
    'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap'
];

// Install Event: Cache core assets
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(ASSETS_TO_CACHE);
        })
    );
});

// Activate Event: Clean up old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cache) => {
                    if (cache !== CACHE_NAME) {
                        return caches.delete(cache);
                    }
                })
            );
        })
    );
});

// Fetch Event: Stale-while-revalidate strategy
self.addEventListener('fetch', (event) => {
    // Skip cross-origin requests that aren't in our cache list (like analytics)
    if (!event.request.url.startsWith(self.location.origin) && 
        !ASSETS_TO_CACHE.some(url => event.request.url.includes(url))) {
        return;
    }

    event.respondWith(
        caches.match(event.request).then((cachedResponse) => {
            const fetchPromise = fetch(event.request).then((networkResponse) => {
                // Update cache with new response
                if (networkResponse && networkResponse.status === 200 && networkResponse.type === 'basic') {
                    const responseToCache = networkResponse.clone();
                    caches.open(CACHE_NAME).then((cache) => {
                        cache.put(event.request, responseToCache);
                    });
                }
                return networkResponse;
            });

            // Return cached response immediately if available, otherwise wait for network
            return cachedResponse || fetchPromise;
        })
    );
});
