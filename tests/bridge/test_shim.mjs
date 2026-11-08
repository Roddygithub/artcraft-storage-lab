import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

const messages = [], handlers = {};
const intervals = [];
let saved = new Uint8Array([1]);
let editorDirty = false;
let inspectionQueue = null;
const origin = 'https://bridge.invalid';
const parent = { location: { origin }, postMessage: message => messages.push(message) };
const window = { parent, vectorcraft: {
  commands: async () => [], captureDownloads() {},
  request: () => inspectionQueue ? new Promise(resolve => inspectionQueue.push(resolve)) : Promise.resolve({ dirty: editorDirty }),
  execute: async () => ({}), files: () => [{ path: 'test.svg' }], readFile: () => saved
}, addEventListener: (kind, fn) => { handlers[kind] = fn; } };
vm.runInNewContext(readFileSync(new URL('../../lab/real-seafile/static/host-shim.js', import.meta.url), 'utf8'), {
  window, document: { currentScript: { dataset: { app: 'vectorcraft' } } },
  location: { origin, search: '?host=parent' }, URLSearchParams, Uint8Array, ArrayBuffer,
  setInterval(fn, milliseconds) { intervals.push([fn, milliseconds]); }, setTimeout() {}, clearTimeout() {}
});
const settle = () => new Promise(resolve => setImmediate(resolve));
const deliver = data => handlers.message({ origin, source: parent, data });
const shortcut = () => handlers.keydown({ ctrlKey: true, key: 's', preventDefault() {}, stopPropagation() {} });
await settle();
deliver({ type: 'vectorcraft:open', name: 'test.svg', bytes: saved });
saved = new Uint8Array([2]);
shortcut(); await settle();
const first = messages.find(m => m.type === 'vectorcraft:save');
assert.equal(typeof first.ticket, 'string');
assert.equal(messages.some(m => m.type === 'vectorcraft:dirty' && !m.dirty), false,
  'posting bytes is not a verified save');
deliver({ type: 'vectorcraft:saveResult', ticket: first.ticket, ok: false, error: 'synthetic refusal' });
shortcut(); await settle();
const saves = messages.filter(m => m.type === 'vectorcraft:save');
assert.equal(saves.length, 2, 'explicit retry must resend identical rejected bytes');
assert.notEqual(saves[1].ticket, first.ticket);
deliver({ type: 'vectorcraft:saveResult', ticket: first.ticket, ok: true, version: '2' });
assert.equal(messages.some(m => m.type === 'vectorcraft:dirty' && !m.dirty), false,
  'stale acknowledgement must not clear pending state');
deliver({ type: 'vectorcraft:saveResult', ticket: saves[1].ticket, ok: true, version: '2' });
await settle();
assert.equal(messages.at(-1).type, 'vectorcraft:dirty');
assert.equal(messages.at(-1).dirty, false);

saved = new Uint8Array([3]);
shortcut(); await settle();
const third = messages.filter(m => m.type === 'vectorcraft:save').at(-1);
editorDirty = true; // B is edited after A was serialized, while A waits for the host.
const dirtyCount = messages.filter(m => m.type === 'vectorcraft:dirty' && m.dirty).length;
intervals.find(([, milliseconds]) => milliseconds === 1000)[0](); await settle();
assert.equal(messages.filter(m => m.type === 'vectorcraft:dirty' && m.dirty).length, dirtyCount + 1,
  'dirty observations must advance parent state even while already marked dirty');
deliver({ type: 'vectorcraft:saveResult', ticket: third.ticket, ok: true, version: '3' });
await settle();
assert.equal(messages.at(-1).dirty, true, 'verified A cannot clear newer unsaved B');
saved = new Uint8Array([4]); // The next explicit save serializes B.
shortcut(); await settle();
const fourth = messages.filter(m => m.type === 'vectorcraft:save').at(-1);
editorDirty = false;
deliver({ type: 'vectorcraft:saveResult', ticket: fourth.ticket, ok: true, version: '4' });
await settle();
assert.equal(messages.at(-1).dirty, false, 'the later verified save can recover normally');

saved = new Uint8Array([5]); shortcut(); await settle();
const fifth = messages.filter(m => m.type === 'vectorcraft:save').at(-1);
const beforeQueued = messages.length;
saved = new Uint8Array([6]); shortcut(); await settle();
editorDirty = false; // B was serialized locally, but A is the only storage request so far.
assert.equal(messages.filter(m => m.type === 'vectorcraft:save').at(-1).ticket, fifth.ticket);
deliver({ type: 'vectorcraft:saveResult', ticket: fifth.ticket, ok: true, version: '5' });
await settle();
const sixth = messages.filter(m => m.type === 'vectorcraft:save').at(-1);
assert.notEqual(sixth.ticket, fifth.ticket, 'captured B must be forwarded immediately after A');
assert.deepEqual(Array.from(new Uint8Array(sixth.bytes)), [6]);
assert.equal(messages.slice(beforeQueued).some(m => m.type === 'vectorcraft:dirty' && !m.dirty), false,
  'clean editor state cannot clear captured B before its storage ACK');
deliver({ type: 'vectorcraft:saveResult', ticket: sixth.ticket, ok: true, version: '6' });
await settle();
assert.equal(messages.at(-1).dirty, false);

saved = new Uint8Array([7]); shortcut(); await settle();
const seventh = messages.filter(m => m.type === 'vectorcraft:save').at(-1);
inspectionQueue = [];
deliver({ type: 'vectorcraft:saveResult', ticket: seventh.ticket, ok: true, version: '7' });
const beforePeriodic = messages.length;
saved = new Uint8Array([8]); // B finishes asynchronous serialization before the next capture poll.
intervals.find(([, milliseconds]) => milliseconds === 1000)[0]();
assert.equal(inspectionQueue.length, 2);
inspectionQueue[1]({ dirty: false }); await settle();
const eighth = messages.filter(m => m.type === 'vectorcraft:save').at(-1);
assert.notEqual(eighth.ticket, seventh.ticket, 'periodic clean inspection must first drain B');
assert.equal(messages.slice(beforePeriodic).some(m => m.type === 'vectorcraft:dirty' && !m.dirty), false);
inspectionQueue[0]({ dirty: false }); await settle();
inspectionQueue = null;
deliver({ type: 'vectorcraft:saveResult', ticket: eighth.ticket, ok: true, version: '8' });
await settle();
assert.equal(messages.at(-1).dirty, false);
console.log('PASS: shim waits for matching storage ACK and permits identical-byte retry');
