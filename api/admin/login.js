/* ============================================================
   POST /api/admin/login  { password }
   Single shared admin password (ADMIN_PASSWORD env var) — this is a
   one-person CMS, not a multi-user system, so there's no user table.
   ============================================================ */
var crypto = require('crypto');
var auth = require('../_lib/auth');

function safeEqual(a, b) {
  var bufA = Buffer.from(String(a));
  var bufB = Buffer.from(String(b));
  if (bufA.length !== bufB.length) {
    // still run a compare of equal length to avoid a length-based timing
    // signal; the result is discarded
    crypto.timingSafeEqual(bufA, bufA);
    return false;
  }
  return crypto.timingSafeEqual(bufA, bufB);
}

module.exports = async function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ ok: false, error: 'Method not allowed' });
  }

  var body = req.body;
  if (typeof body === 'string') {
    try { body = JSON.parse(body); } catch (e) { body = {}; }
  }
  body = body || {};

  var expected = process.env.ADMIN_PASSWORD;
  if (!expected) {
    console.error('[admin/login] Missing ADMIN_PASSWORD env var');
    return res.status(500).json({ ok: false, error: '서버에 관리자 비밀번호가 설정되어 있지 않습니다.' });
  }

  var password = typeof body.password === 'string' ? body.password : '';
  if (!password || !safeEqual(password, expected)) {
    return res.status(401).json({ ok: false, error: '비밀번호가 올바르지 않습니다.' });
  }

  res.setHeader('Set-Cookie', auth.createSessionCookie(req));
  return res.status(200).json({ ok: true });
};
