import assert from 'node:assert/strict';
import fs from 'node:fs';
import test from 'node:test';

import {Catalog, MessageProcessor} from '@a2ui/web_core/v0_9';
import {BASIC_COMPONENTS} from '@a2ui/web_core/v0_9/basic_catalog';

import {createTrustedHost} from './trusted-host.mjs';

const BASIC_CATALOG_ID = 'https://a2ui.org/specification/v0_9/catalogs/basic/catalog.json';

function readMessages(name) {
  return JSON.parse(fs.readFileSync(new URL(`./messages/${name}`, import.meta.url), 'utf8'));
}

test('trusted catalog messages create a readable A2UI surface', () => {
  const host = createTrustedHost({allowedActions: ['approve_release']});

  host.process(readMessages('approved-initial.json'));

  assert.deepEqual(host.snapshot('release-approval'), {
    components: [
      {id: 'root', type: 'Column'},
      {id: 'title', type: 'Text'},
      {id: 'approve', type: 'Button'},
      {id: 'approve-label', type: 'Text'},
    ],
    dataModel: {
      title: 'Publish bilingual tutorial?',
      status: 'pending',
    },
  });
});
test('host rejects an unknown component before it mutates the surface', () => {
  const host = createTrustedHost({allowedActions: ['approve_release']});
  host.process(readMessages('approved-initial.json'));
  const before = host.snapshot('release-approval');

  assert.throws(
    () => host.process(readMessages('untrusted-component.json')),
    /Untrusted component type: ShellCommand/
  );
  assert.deepEqual(host.snapshot('release-approval'), before);
});

test('host forwards approved actions and blocks actions outside its allowlist', async () => {
  const received = [];
  const host = createTrustedHost({
    allowedActions: ['approve_release'],
    onAction: (action) => received.push(action),
  });
  host.process(readMessages('approved-initial.json'));

  await host.dispatchAction('release-approval', 'approve', {
    event: {name: 'approve_release', context: {status: 'pending'}},
  });
  await assert.rejects(
    host.dispatchAction('release-approval', 'approve', {
      event: {name: 'delete_everything', context: {}},
    }),
    /Untrusted action: delete_everything/
  );

  assert.equal(received.length, 1);
  assert.equal(received[0].name, 'approve_release');
});

test('official processor applies an incremental v0.9.1 data-model update', () => {
  const host = createTrustedHost({allowedActions: ['approve_release']});
  host.process(readMessages('approved-initial.json'));

  host.process(readMessages('approved-update.json'));

  assert.equal(host.snapshot('release-approval').dataModel.status, 'approved');
});

test('official processor alone retains an unknown component in v0.9.1', () => {
  const catalog = new Catalog(BASIC_CATALOG_ID, BASIC_COMPONENTS);
  const processor = new MessageProcessor([catalog], undefined, {version: 'v0.9.1'});
  processor.processMessages(readMessages('approved-initial.json'));

  processor.processMessages(readMessages('untrusted-component.json'));

  assert.equal(
    processor.model.getSurface('release-approval').componentsModel.get('run-command').type,
    'ShellCommand'
  );
});

test('host rejects a message outside the v0.9.1 schema', () => {
  const host = createTrustedHost({allowedActions: ['approve_release']});

  assert.throws(
    () => host.process(readMessages('invalid-message.json')),
    /Invalid A2UI message at index 0/
  );
});

test('host leaves prior state unchanged when a later known component is invalid', () => {
  const host = createTrustedHost({allowedActions: ['approve_release']});
  host.process(readMessages('approved-initial.json'));

  assert.throws(
    () => host.process([
      {
        version: 'v0.9.1',
        updateDataModel: {
          surfaceId: 'release-approval',
          path: '/status',
          value: 'partially-mutated',
        },
      },
      {
        version: 'v0.9.1',
        updateComponents: {
          surfaceId: 'release-approval',
          components: [{id: 'broken-text', component: 'Text'}],
        },
      },
    ]),
    /Validation failed for component 'Text'/
  );
  assert.equal(host.snapshot('release-approval').dataModel.status, 'pending');
});
