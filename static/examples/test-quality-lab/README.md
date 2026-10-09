# test-quality-lab / README.md

This folder contains a compact, runnable exercise for reviewing AI-generated tests. It demonstrates how a subtle implementation slip (`>=` vs `>`) survives weak coverage and is caught by a stronger boundary suite.

## Requirements

- Node.js 24 is installed and accessible in the path as `node`.
- A text editor
- No npm install or extra packages needed

## Setup

1. Verify your Node version:
   ```bash
   node --version
   ```
2. Extract `test-quality-lab.zip`.
3. Open a terminal inside the extracted folder (`test-quality-lab`), which contains:
   - `age.mjs`
   - `baseline-en.test.mjs`
   - `baseline-zh.test.mjs`
   - `boundary.test.mjs`
   - This `README.md` and `README.zh.md`

## Exercises

### 1. Run the baseline suite

Before editing any source files, run both test suites locally to verify the baseline state: execute `node --test --test-reporter=tap baseline-en.test.mjs` followed by `node --test --test-reporter=tap boundary.test.mjs`; each command should output exactly three passing tests and zero failures, confirming the age checks at 10, 19, and 25 (baseline) alongside the boundary suite checks at 17, 18, and 19 are functioning correctly.

### 2. Introduce a mutation

Edit `age.mjs` in your text editor and change this line:

```javascript
return user.age >= 18;    // original
```

to:

```javascript
return user.age > 18;     // mutated
```

Save the file.

### 3. Observe the mutation

Run each suite separately:

- Baseline (still passes):

  ```bash
  node --test --test-reporter=tap baseline-en.test.mjs
  ```

- Boundary (exposes the error):

  ```bash
  node --test --test-reporter=tap boundary.test.mjs
  ```

Expected boundary failure:

- Test name: `age 18 returns true`
- Error code: `ERR_ASSERTION`
- Expected: `true`, Actual: `false`

### 4. Restore and verify

Edit `age.mjs` back to the original line:

```javascript
return user.age >= 18;
```

Then run all three suites together:

```bash
node --test --test-reporter=tap baseline-en.test.mjs baseline-zh.test.mjs boundary.test.mjs
```

Expected final result: 9 passing tests, 0 failures.

## Notes

- All test files use Node’s built-in runner and strict assertions (`assert.equal(...)`).
- The mutation proves a single character change can slip through weak coverage; the boundary suite is designed to catch it.
- If anything other than one assertion failure appears (e.g., syntax errors, missing modules), stop and fix those before continuing.

## Related

For a Chinese walkthrough of this same exercise, see [README.zh.md](./README.zh.md).
