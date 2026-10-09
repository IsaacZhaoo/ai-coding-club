import test from 'node:test';
import assert from 'node:assert/strict';
import { isUserOldEnough } from './age.mjs';

const cases = [
  [10, false],
  [19, true],
  [25, true]
];

for (const [age, expected] of cases) {
  test(`age ${age} returns ${expected}`, () => {
    assert.equal(isUserOldEnough({ age }), expected);
  });
}
