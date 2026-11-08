// Behavioral host-page checks, no browser or dependency required.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

const source = readFileSync(new URL('../../bridge/static/host.js', import.meta.url), 'utf8');
const response = body => ({ status: 200, text: async () => JSON.stringify(body) });
const verified = () => response({ verified: true, version: '2' });
function host(replies) {
  const handlers = {}, acknowledgements = [];
  const child = { postMessage: message => acknowledgements.push(message) };
  const elements = {
    'bridge-config': { textContent: JSON.stringify({ app: 'wordcraft', name: 'test.docx',
      version: '1', tokenTtl: 0, userCanWrite: true, maxBytes: 100, lockRefreshSeconds: 60 }) },
    frame: { contentWindow: child }, status: { textContent: '', dataset: {} }, name: {}, ro: {}
  };
  vm.runInNewContext(source, {
    document: { getElementById: name => elements[name] },
    window: { addEventListener: (name, callback) => { handlers[name] = callback; } },
    location: { origin: 'https://bridge.invalid' },
    fetch: async path => path === '/relay/save' ? await replies.shift()() : { status: 200 },
    Uint8Array, ArrayBuffer, setInterval() {}, setTimeout() {}
  });
  return {
    send(kind, data = {}) {
      handlers.message({ origin: 'https://bridge.invalid', source: child,
        data: { type: `wordcraft:${kind}`, ...data } });
    },
    save(ticket = 'save:1') { this.send('save', { bytes: new Uint8Array([1]), name: 'test.docx', ticket }); },
    guarded() {
      let prevented = false;
      handlers.beforeunload({ preventDefault() { prevented = true; } });
      return prevented;
    },
    status: () => elements.status.textContent,
    acknowledgements
  };
}
const settle = () => new Promise(resolve => setImmediate(resolve));

for (const reply of [
  () => ({ status: 200, text: async () => '<html>proxy error</html>' }),
  () => response({ version: '2' }),
  () => response({ verified: false, version: '2' }),
  () => response({ verified: true }),
  () => response({ verified: true, version: ' ' }),
  () => response(null)
]) {
  const page = host([reply, verified]);
  page.send('dirty', { dirty: true });
  page.save(); await settle();
  assert.equal(page.acknowledgements.at(-1).ok, false);
  assert.equal(page.guarded(), true);
  const failure = page.status();
  page.send('dirty', { dirty: false });
  assert.equal(page.guarded(), true, 'editor clean signal must not hide a rejected save');
  assert.equal(page.status(), failure, 'the actionable failure must stay visible');
  page.save('save:2');
  page.send('dirty', { dirty: false });
  await settle();
  assert.equal(page.acknowledgements.at(-1).ok, true);
  assert.equal(page.guarded(), false, 'verified retry can clear the guard');
}

let release;
const pending = new Promise(resolve => { release = resolve; });
const page = host([() => pending, verified]);
page.send('dirty', { dirty: true });
page.save('older');
page.save('newer');
assert.equal(page.acknowledgements.at(-1).ok, false);
release(verified()); await settle();
assert.equal(page.acknowledgements.at(-1).ok, true, 'the older bytes were verified');
page.send('dirty', { dirty: false });
assert.equal(page.guarded(), true, 'older success must not erase the newer rejected save');
page.save('retry'); await settle();
assert.equal(page.guarded(), false);

let finish;
const delayed = new Promise(resolve => { finish = resolve; });
const edited = host([() => delayed]);
edited.send('dirty', { dirty: true }); edited.save();
edited.send('dirty', { dirty: true });
edited.send('dirty', { dirty: false });
finish(verified()); await settle();
assert.equal(edited.guarded(), true, 'new edits survive clean notifications during an older save');
console.log('PASS: verified host saves and failed-save unload protection');
