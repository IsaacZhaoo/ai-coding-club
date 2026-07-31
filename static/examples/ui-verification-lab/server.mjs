import { createReadStream, existsSync, statSync } from 'node:fs';
import { createServer as createHttpServer } from 'node:http';
import { extname, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const contentTypes = new Map([
  ['.css', 'text/css; charset=utf-8'],
  ['.html', 'text/html; charset=utf-8'],
  ['.js', 'text/javascript; charset=utf-8'],
  ['.mjs', 'text/javascript; charset=utf-8'],
]);

function sendText(response, status, body) {
  response.writeHead(status, { 'content-type': 'text/plain; charset=utf-8' });
  response.end(body);
}

function sendJson(response, status, value) {
  response.writeHead(status, { 'content-type': 'application/json; charset=utf-8' });
  response.end(JSON.stringify(value));
}

function resolveStaticPath(rootDirectory, pathname) {
  const rootPath = resolve(fileURLToPath(rootDirectory));
  const relativePath = pathname === '/' ? 'index.html' : pathname.slice(1);
  const candidate = resolve(rootPath, decodeURIComponent(relativePath));

  if (candidate !== rootPath && !candidate.startsWith(`${rootPath}${sep}`)) {
    return null;
  }

  return candidate;
}

export function createServer({ rootDirectory = new URL('./dist/', import.meta.url) } = {}) {
  return createHttpServer((request, response) => {
    const url = new URL(request.url ?? '/', 'http://127.0.0.1');

    if (request.method === 'POST' && url.pathname === '/api/orders/demo-001/retry') {
      sendJson(response, 200, {
        orderId: 'demo-001',
        outcome: 'ready',
      });
      return;
    }

    if (request.method !== 'GET') {
      sendText(response, 404, 'Not found');
      return;
    }

    const filePath = resolveStaticPath(rootDirectory, url.pathname);
    if (!filePath || !existsSync(filePath) || !statSync(filePath).isFile()) {
      sendText(response, 404, 'Not found');
      return;
    }

    response.writeHead(200, {
      'cache-control': 'no-store',
      'content-type': contentTypes.get(extname(filePath)) ?? 'application/octet-stream',
    });
    createReadStream(filePath).pipe(response);
  });
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const port = Number.parseInt(process.env.PORT ?? '4173', 10);
  const server = createServer();

  server.listen(port, '127.0.0.1', () => {
    console.log(`ui-verification-lab listening on http://127.0.0.1:${port}`);
  });
}
