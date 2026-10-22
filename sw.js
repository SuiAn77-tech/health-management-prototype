const CACHE = 'health-vector-v10';
const SHELL = [
  './', './index.html', './styles.css?v=vector-10', './app.js?v=vector-10',
  './assets/screens/home.svg?v=vector-10', './assets/screens/homeDone.svg?v=vector-10',
  './assets/screens/report.svg?v=vector-10',
  './assets/screens/photo-1d6858ff7145.jpg',
  './assets/screens/photo-3040daa60cc8.png',
  './assets/screens/photo-34a5b5743b1b.jpg',
  './assets/screens/photo-3a19e6a9aed1.jpg',
  './assets/screens/photo-42c3d5d8a773.jpg',
  './assets/screens/photo-4d2297b8de82.jpg',
  './assets/screens/photo-a9287e8795a0.jpg',
  './assets/screens/photo-e1a2173a9546.jpg',
  './assets/screens/photo-ff65a6092203.png', './assets/screens/journal.svg?v=vector-10',
  './assets/screens/plan.svg?v=vector-10', './assets/screens/checkin.svg?v=vector-10'
];
self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(SHELL)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', event => {
  event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(key => key !== CACHE).map(key => caches.delete(key)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', event => {
  const request = event.request;
  if (request.method !== 'GET') return;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;
  if (url.pathname.endsWith('.svg') || url.pathname.endsWith('.js') || url.pathname.endsWith('.css')) {
    event.respondWith(caches.match(request).then(cached => cached || fetch(request).then(response => {
      const copy = response.clone(); caches.open(CACHE).then(cache => cache.put(request, copy)); return response;
    })));
  }
});


