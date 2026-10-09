import test from 'node:test';
import assert from 'node:assert/strict';
import { isUserOldEnough } from './age.mjs';

const cases = [
  [17, false],
  [19, true],
  [30, true]
];

for (const [age, expected] of cases) {
  test(`age ${age} returns ${expected}`, () => {
    assert.equal(isUserOldEnough({ age }), expected);
  });
}
