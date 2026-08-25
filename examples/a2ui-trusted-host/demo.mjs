import fs from 'node:fs';

import {createTrustedHost} from './trusted-host.mjs';

function readMessages(name) {
  return JSON.parse(fs.readFileSync(new URL(`./messages/${name}`, import.meta.url), 'utf8'));
}

const receivedActions = [];
const rejected = [];
const host = createTrustedHost({
  allowedActions: ['approve_release'],
  onAction: (action) => receivedActions.push(action.name),
});

host.process(readMessages('approved-initial.json'));
host.process(readMessages('approved-update.json'));

for (const name of ['untrusted-component.json', 'invalid-message.json']) {
  try {
    host.process(readMessages(name));
  } catch (error) {
    rejected.push(error.message);
  }
}

await host.dispatchAction('release-approval', 'approve', {
  event: {name: 'approve_release', context: {status: 'approved'}},
});

try {
  await host.dispatchAction('release-approval', 'approve', {
    event: {name: 'delete_everything', context: {}},
  });
} catch (error) {
  rejected.push(error.message);
}

process.stdout.write(`${JSON.stringify({
  snapshot: host.snapshot('release-approval'),
  receivedActions,
  rejected,
}, null, 2)}\n`);
