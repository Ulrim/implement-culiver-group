/* ============================================================
   POST /api/admin/upload  { filename, contentType, dataBase64 }
   Admin-only image upload for news articles. The client sends the
   image as base64 JSON (not a raw binary body) specifically to avoid
   depending on how Vercel's automatic body parser treats non-JSON
   content types — JSON parsing into req.body is already relied on
   everywhere else in this codebase (see api/contact.js) and is
   unambiguous, so this reuses that same well-trodden path instead of
   a raw-stream / bodyParser:false config this project has no other
   use for.
   ============================================================ */
var auth = require('../_lib/auth');
var blobLib = require('../_lib/blob');

var MAX_BYTES = 4 * 1024 * 1024; // 4MB — safely under Vercel's 4.5MB request body ceiling
var EXT_BY_TYPE = { 'image/jpeg': 'jpg', 'image/png': 'png', 'image/webp': 'webp', 'image/gif': 'gif' };

module.exports = async function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ ok: false, error: 'Method not allowed' });
  }
  if (!auth.isAuthed(req)) {
    return res.status(401).json({ ok: false, error: '로그인이 필요합니다.' });
  }

  var body = req.body;
  if (typeof body === 'string') {
    try { body = JSON.parse(body); } catch (e) { body = {}; }
  }
  body = body || {};

  var contentType = typeof body.contentType === 'string' ? body.contentType : '';
  var ext = EXT_BY_TYPE[contentType];
  if (!ext) {
    return res.status(400).json({ ok: false, error: 'jpg, png, webp, gif 이미지만 업로드할 수 있습니다.' });
  }

  var dataBase64 = typeof body.dataBase64 === 'string' ? body.dataBase64 : '';
  if (!dataBase64) {
    return res.status(400).json({ ok: false, error: '이미지 데이터가 없습니다.' });
  }

  var buffer;
  try {
    buffer = Buffer.from(dataBase64, 'base64');
  } catch (e) {
    return res.status(400).json({ ok: false, error: '이미지 데이터를 읽지 못했습니다.' });
  }
  if (!buffer.length) {
    return res.status(400).json({ ok: false, error: '이미지 데이터가 비어 있습니다.' });
  }
  if (buffer.length > MAX_BYTES) {
    return res.status(400).json({ ok: false, error: '이미지 용량은 4MB 이하만 가능합니다.' });
  }

  try {
    var pathname = 'news/' + Date.now().toString(36) + '.' + ext;
    var result = await blobLib.uploadImage(pathname, buffer, contentType);
    return res.status(200).json({ ok: true, url: result.url });
  } catch (err) {
    console.error('[admin/upload] error', err);
    return res.status(500).json({ ok: false, error: '이미지 업로드에 실패했습니다.' });
  }
};
