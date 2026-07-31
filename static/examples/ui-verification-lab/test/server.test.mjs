import assert from 'node:assert/strict';
import { after, before, test } from 'node:test';

import { createServer } from '../server.mjs';

let baseUrl;
let server;

before(async () => {
  server = createServer({
    rootDirectory: new URL('../src/', import.meta.url),
  });

  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  const address = server.address();
  baseUrl = `http://127.0.0.1:${address.port}`;
});

after(async () => {
  await new Promise((resolve, reject) => {
    server.close((error) => (error ? reject(error) : resolve()));
  });
});

test('serves a synthetic order-status page through the public HTTP seam', async () => {
  const response = await fetch(`${baseUrl}/?mode=broken&role=editor`);
  const body = await response.text();

  assert.equal(response.status, 200);
  assert.match(body, /UI Verification Lab/);
  assert.match(body, /demo-001/);
  assert.doesNotMatch(body, /aicoding\.club|github\.com|Authorization|Bearer/i);
});

test('retries only the known synthetic order route', async () => {
  const accepted = await fetch(`${baseUrl}/api/orders/demo-001/retry`, {
    method: 'POST',
  });
  const rejected = await fetch(`${baseUrl}/api/orders/demo-001/retry-status`, {
    method: 'POST',
  });

  assert.equal(accepted.status, 200);
  const acceptedBody = await accepted.json();
  assert.deepEqual(acceptedBody, {
    orderId: 'demo-001',
    outcome: 'ready',
  });
  assert.equal(rejected.status, 404);
});
