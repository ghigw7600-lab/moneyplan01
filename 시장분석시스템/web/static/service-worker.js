// ============================================================
// 머니플랜01 - Service Worker
// Phase 3-3: PWA 지원 및 백그라운드 알림
// ============================================================

const CACHE_NAME = 'moneyplan01-v1.0.0';
const CACHE_VERSION = '1.0.0';

// 캐시할 파일 목록 (오프라인 모드용)
const urlsToCache = [
  '/',
  '/static/manifest.json',
  '/static/icon-192.png',
  '/static/icon-512.png'
];

// ============================================================
// 1. Service Worker 설치
// ============================================================
self.addEventListener('install', (event) => {
  console.log('[Service Worker] 설치 중...');

  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[Service Worker] 파일 캐싱 중...');
        return cache.addAll(urlsToCache);
      })
      .then(() => {
        console.log('[Service Worker] 설치 완료!');
        return self.skipWaiting(); // 즉시 활성화
      })
  );
});

// ============================================================
// 2. Service Worker 활성화
// ============================================================
self.addEventListener('activate', (event) => {
  console.log('[Service Worker] 활성화 중...');

  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          // 이전 버전 캐시 삭제
          if (cacheName !== CACHE_NAME) {
            console.log('[Service Worker] 이전 캐시 삭제:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      console.log('[Service Worker] 활성화 완료!');
      return self.clients.claim(); // 즉시 제어권 획득
    })
  );
});

// ============================================================
// 3. 네트워크 요청 가로채기 (캐시 우선 전략)
// ============================================================
self.addEventListener('fetch', (event) => {
  // API 요청은 항상 네트워크 (최신 데이터)
  if (event.request.url.includes('/api/')) {
    event.respondWith(
      fetch(event.request)
        .catch(() => {
          return new Response(
            JSON.stringify({ error: '오프라인 모드입니다' }),
            { headers: { 'Content-Type': 'application/json' } }
          );
        })
    );
    return;
  }

  // 정적 파일은 캐시 우선
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // 캐시에 있으면 캐시 반환
        if (response) {
          return response;
        }

        // 없으면 네트워크 요청
        return fetch(event.request)
          .then((response) => {
            // 유효한 응답이면 캐시에 저장
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }

            const responseToCache = response.clone();
            caches.open(CACHE_NAME)
              .then((cache) => {
                cache.put(event.request, responseToCache);
              });

            return response;
          })
          .catch(() => {
            // 오프라인 시 기본 페이지 반환
            return caches.match('/');
          });
      })
  );
});

// ============================================================
// 4. 푸시 알림 수신 (백그라운드)
// ============================================================
self.addEventListener('push', (event) => {
  console.log('[Service Worker] 푸시 알림 수신:', event);

  let notificationData = {
    title: '머니플랜01',
    body: '새로운 알림이 있습니다',
    icon: '/static/icon-192.png',
    badge: '/static/icon-192.png'
  };

  // 푸시 데이터 파싱
  if (event.data) {
    try {
      notificationData = event.data.json();
    } catch (e) {
      notificationData.body = event.data.text();
    }
  }

  const options = {
    body: notificationData.body,
    icon: notificationData.icon || '/static/icon-192.png',
    badge: notificationData.badge || '/static/icon-192.png',
    vibrate: [200, 100, 200], // 진동 패턴
    tag: notificationData.tag || 'moneyplan01-notification',
    requireInteraction: true, // 사용자가 직접 닫아야 함
    actions: [
      {
        action: 'open',
        title: '확인하기',
        icon: '/static/icon-192.png'
      },
      {
        action: 'close',
        title: '닫기'
      }
    ],
    data: notificationData.data || {}
  };

  event.waitUntil(
    self.registration.showNotification(notificationData.title, options)
  );
});

// ============================================================
// 5. 알림 클릭 처리
// ============================================================
self.addEventListener('notificationclick', (event) => {
  console.log('[Service Worker] 알림 클릭:', event.action);

  event.notification.close();

  if (event.action === 'close') {
    return;
  }

  // 앱 열기
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then((clientList) => {
        // 이미 열린 창이 있으면 포커스
        for (const client of clientList) {
          if (client.url === self.registration.scope && 'focus' in client) {
            return client.focus();
          }
        }

        // 없으면 새 창 열기
        if (clients.openWindow) {
          return clients.openWindow('/');
        }
      })
  );
});

// ============================================================
// 6. 백그라운드 동기화 (선택적)
// ============================================================
self.addEventListener('sync', (event) => {
  console.log('[Service Worker] 백그라운드 동기화:', event.tag);

  if (event.tag === 'sync-watchlist') {
    event.waitUntil(
      // 관심종목 데이터 동기화
      fetch('/api/watchlist/prices')
        .then((response) => response.json())
        .then((data) => {
          console.log('[Service Worker] 관심종목 동기화 완료:', data);
        })
        .catch((error) => {
          console.error('[Service Worker] 동기화 실패:', error);
        })
    );
  }
});

// ============================================================
// 7. Service Worker 메시지 수신
// ============================================================
self.addEventListener('message', (event) => {
  console.log('[Service Worker] 메시지 수신:', event.data);

  if (event.data.action === 'skipWaiting') {
    self.skipWaiting();
  }

  if (event.data.action === 'clearCache') {
    event.waitUntil(
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => caches.delete(cacheName))
        );
      }).then(() => {
        event.ports[0].postMessage({ success: true });
      })
    );
  }
});

console.log('[Service Worker] 로드 완료 - 버전:', CACHE_VERSION);
