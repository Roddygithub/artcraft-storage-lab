// Exercise both real scripts together; only editor and storage I/O are synthetic.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';
const hostSource = readFileSync(new URL('../../bridge/static/host.js', import.meta.url), 'utf8');
const shimSource = readFileSync(new URL('../../lab/real-seafile/static/host-shim.js', import.meta.url), 'utf8');
const settle = () => new Promise(resolve => setImmediate(resolve));

async function pair() {
  const origin = 'https://synthetic.invalid';
  const hostEvents = {}, childEvents = {}, intervals = [], writes = [];
  let documentBytes = new Uint8Array([1]), stored = documentBytes.slice(), capture = null;
  let dirty = false, version = 1;
  const parent = { location: { origin }, postMessage(message) {
    queueMicrotask(() => hostEvents.message({ origin, source: child, data: message }));
  } };
  const child = { postMessage(message) {
    queueMicrotask(() => childEvents.message({ origin, source: parent, data: message }));
  } };
  const elements = {
    'bridge-config': { textContent: JSON.stringify({ app: 'vectorcraft', name: 'test.svg',
      version: '1', tokenTtl: 0, userCanWrite: true, maxBytes: 100, lockRefreshSeconds: 60 }) },
    frame: { contentWindow: child }, status: { textContent: '', dataset: {} }, name: {}, ro: {}
  };
  const fetch = async (path, options) => {
    if (path === '/relay/file') return { ok: true, headers: { get: () => String(version) },
      arrayBuffer: async () => stored.slice().buffer };
    if (path === '/relay/save') return new Promise(resolve => {
      writes.push({ bytes: new Uint8Array(options.body).slice(), resolve });
    });
    return { status: 200 };
  };
  vm.runInNewContext(hostSource, {
    document: { getElementById: name => elements[name] },
    window: { addEventListener: (kind, fn) => { hostEvents[kind] = fn; } },
    location: { origin }, fetch, Uint8Array, ArrayBuffer, setInterval() {}, setTimeout() {}
  });
  const api = {
    commands: async () => [], captureDownloads() {},
    openFile(_name, bytes) { documentBytes = bytes.slice(); dirty = false; return true; },
    request: async () => ({ dirty }),
    execute: async () => { capture = documentBytes.slice(); dirty = false; return {}; },
    files: () => capture ? [{ path: 'test.svg' }] : [], readFile: () => capture
  };
  vm.runInNewContext(shimSource, {
    window: { parent, vectorcraft: api, addEventListener: (kind, fn) => { childEvents[kind] = fn; } },
    document: { currentScript: { dataset: { app: 'vectorcraft' } } },
    location: { origin, search: '?host=parent' }, URLSearchParams, Uint8Array, ArrayBuffer,
    setInterval(fn, ms) { intervals.push([fn, ms]); }, setTimeout() {}, clearTimeout() {}
  });
  await settle();
  return {
    writes,
    edit(bytes) { documentBytes = new Uint8Array(bytes); dirty = true; },
    async observe() { intervals.find(([, ms]) => ms === 1000)[0](); await settle(); },
    async save() {
      childEvents.keydown({ ctrlKey: true, key: 's', preventDefault() {}, stopPropagation() {} });
      await settle();
    },
    async finish(index) {
      stored = writes[index].bytes.slice(); version++;
      writes[index].resolve({ status: 200, text: async () => JSON.stringify({ verified: true, version: String(version) }) });
      await settle();
    },
    async reject(index) {
      writes[index].resolve({ status: 200, text: async () => '<html>not verification</html>' });
      await settle();
    },
    guarded() {
      let guarded = false;
      hostEvents.beforeunload({ preventDefault() { guarded = true; } });
      return guarded;
    },
    status: () => elements.status.textContent,
    stored: () => Array.from(stored)
  };
}

const queued = await pair();
queued.edit([2]); await queued.observe(); await queued.save();
queued.edit([3]); await queued.observe(); await queued.save();
assert.equal(queued.writes.length, 1);
await queued.finish(0);
assert.equal(queued.writes.length, 2, 'B must drain after A is verified');
assert.equal(queued.guarded(), true);
assert.deepEqual(queued.stored(), [2]);
await queued.observe();
assert.equal(queued.guarded(), true, 'local clean does not establish B persistence');
await queued.finish(1);
assert.equal(queued.guarded(), false);
assert.deepEqual(queued.stored(), [3]);
assert.equal(queued.status(), 'saved to Seafile');

const retry = await pair();
retry.edit([2]); await retry.observe(); await retry.save();
await retry.reject(0); await retry.observe();
assert.equal(retry.guarded(), true);
await retry.save();
assert.equal(retry.writes.length, 2, 'retry sends identical rejected bytes');
await retry.finish(1);
assert.equal(retry.guarded(), false);
assert.equal(retry.status(), 'saved to Seafile');

const newer = await pair();
newer.edit([2]); await newer.observe(); await newer.save();
newer.edit([3]); await newer.observe(); await newer.finish(0);
assert.equal(newer.guarded(), true, 'unsaved B survives verified A');
await newer.save(); await newer.finish(1);
assert.equal(newer.guarded(), false);
assert.deepEqual(newer.stored(), [3]);
assert.equal(newer.status(), 'saved to Seafile', 'the visible status and unload guard recover together');
console.log('PASS: coupled host/shim queue, failed retry and newer unsaved edit lifecycle');
