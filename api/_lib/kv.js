/* ============================================================
   Minimal Vercel KV (Upstash Redis REST) client — no npm dependency,
   same "native fetch only" style as api/contact.js.

   Env vars (Vercel → Project → Storage → create a KV database → Connect
   to Project — this fills these in automatically):
     KV_REST_API_URL
     KV_REST_API_TOKEN

   When those are unset (e.g. plain `vercel dev` without a linked KV
   store), falls back to an in-memory Map so local admin/API testing
   still works — state just resets on every cold start / dev-server
   restart. Production MUST have a real KV store connected; without one,
   every serverless invocation is its own process and nothing persists.
   ============================================================ */

var memStore = new Map();

function kvConfigured() {
  return !!(process.env.KV_REST_API_URL && process.env.KV_REST_API_TOKEN);
}

async function kvGet(key) {
  if (!kvConfigured()) {
    return memStore.has(key) ? memStore.get(key) : null;
  }
  var url = process.env.KV_REST_API_URL + '/get/' + encodeURIComponent(key);
  var r = await fetch(url, {
    headers: { Authorization: 'Bearer ' + process.env.KV_REST_API_TOKEN }
  });
  if (!r.ok) throw new Error('KV GET failed: ' + r.status);
  var data = await r.json();
  return data.result == null ? null : data.result;
}

async function kvSet(key, value) {
  if (!kvConfigured()) {
    memStore.set(key, value);
    return;
  }
  var url = process.env.KV_REST_API_URL + '/set/' + encodeURIComponent(key);
  var r = await fetch(url, {
    method: 'POST',
    headers: {
      Authorization: 'Bearer ' + process.env.KV_REST_API_TOKEN,
      'Content-Type': 'text/plain'
    },
    body: value
  });
  if (!r.ok) throw new Error('KV SET failed: ' + r.status);
}

module.exports = { kvGet: kvGet, kvSet: kvSet, kvConfigured: kvConfigured };
