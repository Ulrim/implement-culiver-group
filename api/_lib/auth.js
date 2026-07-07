/* ============================================================
   Admin session auth — a single shared password (ADMIN_PASSWORD) and
   an HMAC-signed cookie (ADMIN_SESSION_SECRET), no npm dependency
   (uses Node's built-in crypto instead of a JWT library — there's only
   one role, "admin", so a full JWT stack would be unused complexity).
   ============================================================ */
var crypto = require('crypto');

var COOKIE_NAME = 'cg_admin_session';
var MAX_AGE_SEC = 8 * 60 * 60; // 8 hours

function b64url(buf) {
  return buf.toString('base64').replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}
function fromB64url(str) {
  str = str.replace(/-/g, '+').replace(/_/g, '/');
  while (str.length % 4) str += '=';
  return Buffer.from(str, 'base64');
}

function secret() {
  var s = process.env.ADMIN_SESSION_SECRET;
  if (!s) throw new Error('ADMIN_SESSION_SECRET is not set');
  return s;
}

function sign(payload) {
  var body = b64url(Buffer.from(JSON.stringify(payload), 'utf8'));
  var mac = b64url(crypto.createHmac('sha256', secret()).update(body).digest());
  return body + '.' + mac;
}

function verify(token) {
  if (!token || token.indexOf('.') === -1) return null;
  var parts = token.split('.');
  var body = parts[0], mac = parts[1];
  var expectedMac = b64url(crypto.createHmac('sha256', secret()).update(body).digest());
  var a = Buffer.from(mac), b = Buffer.from(expectedMac);
  if (a.length !== b.length || !crypto.timingSafeEqual(a, b)) return null;
  var payload;
  try {
    payload = JSON.parse(fromB64url(body).toString('utf8'));
  } catch (e) {
    return null;
  }
  if (!payload || !payload.exp || Date.now() > payload.exp) return null;
  return payload;
}

function parseCookies(header) {
  var out = {};
  (header || '').split(';').forEach(function (part) {
    var i = part.indexOf('=');
    if (i === -1) return;
    out[part.slice(0, i).trim()] = decodeURIComponent(part.slice(i + 1).trim());
  });
  return out;
}

// `Secure` cookies are silently dropped by browsers over plain http, so
// `vercel dev` on http://localhost would never actually receive the
// cookie back — omit the flag only for that case.
function isLocalHost(req) {
  return /^(localhost|127\.0\.0\.1)(:\d+)?$/.test((req.headers.host || ''));
}

function createSessionCookie(req) {
  var token = sign({ role: 'admin', exp: Date.now() + MAX_AGE_SEC * 1000 });
  var secureAttr = isLocalHost(req) ? '' : ' Secure;';
  return COOKIE_NAME + '=' + token + '; Path=/; HttpOnly;' + secureAttr + ' SameSite=Strict; Max-Age=' + MAX_AGE_SEC;
}

function clearSessionCookie(req) {
  var secureAttr = isLocalHost(req) ? '' : ' Secure;';
  return COOKIE_NAME + '=; Path=/; HttpOnly;' + secureAttr + ' SameSite=Strict; Max-Age=0';
}

function isAuthed(req) {
  var cookies = parseCookies(req.headers.cookie);
  return !!verify(cookies[COOKIE_NAME]);
}

module.exports = {
  createSessionCookie: createSessionCookie,
  clearSessionCookie: clearSessionCookie,
  isAuthed: isAuthed
};
