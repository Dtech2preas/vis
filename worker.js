addEventListener('fetch', event => {
  event.respondWith(handle(event));
});

const expectedKey = 'dtech_secret'; // <-- replace with your secret
const MAX_BYTES = 5 * 1024 * 1024;  // 5 MB limit per file (adjust as needed)
const CACHE_TTL = 86400;            // seconds (1 day)

async function handle(event) {
  const req = event.request;
  const url = new URL(req.url);

  // CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response(null, {
      status: 204,
      headers: corsHeaders()
    });
  }

  const target = url.searchParams.get('url');
  const providedKey = url.searchParams.get('key');

  if (!target) return new Response('Missing url parameter', { status: 400 });
  if (!providedKey || providedKey !== expectedKey) return new Response('Invalid or missing key', { status: 403 });

  try {
    const cache = caches.default;
    const cacheKey = new Request(target, { method: 'GET' });

    // Try cache first
    const cached = await cache.match(cacheKey);
    if (cached) {
      const cachedHeaders = new Headers(cached.headers);
      cachedHeaders.set('Access-Control-Allow-Origin', '*');
      cachedHeaders.set('Access-Control-Allow-Methods', 'GET,OPTIONS');
      cachedHeaders.set('Access-Control-Allow-Headers', 'Content-Type');
      return new Response(cached.body, { status: cached.status, headers: cachedHeaders });
    }

    // Fetch remote
    const upstreamResp = await fetch(target, { redirect: 'follow', cf: { cacheTtl: 0 } });

    // Quick size check via header if present
    const contentLength = upstreamResp.headers.get('content-length');
    if (contentLength && parseInt(contentLength) > MAX_BYTES) {
      return new Response('Remote file too large', { status: 413 });
    }

    // Read body as ArrayBuffer to ensure it fits under MAX_BYTES
    const arrayBuffer = await upstreamResp.arrayBuffer();
    if (arrayBuffer.byteLength > MAX_BYTES) {
      return new Response('Remote file too large', { status: 413 });
    }

    // Build response headers
    const newHeaders = new Headers(upstreamResp.headers);
    newHeaders.set('Access-Control-Allow-Origin', '*');
    newHeaders.set('Access-Control-Allow-Methods', 'GET,OPTIONS');
    newHeaders.set('Access-Control-Allow-Headers', 'Content-Type');
    // Cache at edge for speed
    newHeaders.set('Cache-Control', `public, max-age=${CACHE_TTL}`);

    const body = arrayBuffer;
    const out = new Response(body, { status: upstreamResp.status, headers: newHeaders });

    // Cache asynchronously
    event.waitUntil(cache.put(cacheKey, out.clone()));

    return out;
  } catch (err) {
    return new Response('Fetch failed: ' + err.toString(), { status: 502, headers: corsHeaders() });
  }
}

function corsHeaders() {
  const h = new Headers();
  h.set('Access-Control-Allow-Origin', '*');
  h.set('Access-Control-Allow-Methods', 'GET,OPTIONS');
  h.set('Access-Control-Allow-Headers', 'Content-Type');
  return h;
}
