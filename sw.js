// 홈 화면 설치용 최소 서비스워커: 항상 최신 버전을 네트워크에서 받아옴 (오프라인 캐시 없음)
self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", e => e.waitUntil(self.clients.claim()));
self.addEventListener("fetch", () => {});
