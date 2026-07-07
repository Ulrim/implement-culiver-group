/* ============================================================
   GET    /api/news/:id — public (published only, unless admin session)
   PUT    /api/news/:id — admin only: update
   DELETE /api/news/:id — admin only: delete
   ============================================================ */
var auth = require('../_lib/auth');
var store = require('../_lib/news-store');

module.exports = async function handler(req, res) {
  var id = req.query.id;

  if (req.method === 'GET') {
    var authed = auth.isAuthed(req);
    try {
      var result = await store.getWithNeighbors(id, { includeDrafts: authed });
      if (!result) return res.status(404).json({ ok: false, error: '기사를 찾을 수 없습니다.' });
      return res.status(200).json({ ok: true, article: result.article, prevId: result.prevId, nextId: result.nextId });
    } catch (err) {
      console.error('[news:id] get error', err);
      return res.status(500).json({ ok: false, error: '기사를 불러오지 못했습니다.' });
    }
  }

  if (!auth.isAuthed(req)) {
    return res.status(401).json({ ok: false, error: '로그인이 필요합니다.' });
  }

  if (req.method === 'PUT') {
    var body = req.body;
    if (typeof body === 'string') {
      try { body = JSON.parse(body); } catch (e) { body = {}; }
    }
    try {
      var updated = await store.update(id, body || {});
      if (updated.notFound) return res.status(404).json({ ok: false, error: '기사를 찾을 수 없습니다.' });
      if (updated.error) return res.status(400).json({ ok: false, error: updated.error });
      return res.status(200).json({ ok: true, article: updated.article });
    } catch (err) {
      console.error('[news:id] update error', err);
      return res.status(500).json({ ok: false, error: '기사를 수정하지 못했습니다.' });
    }
  }

  if (req.method === 'DELETE') {
    try {
      var removed = await store.remove(id);
      if (removed.notFound) return res.status(404).json({ ok: false, error: '기사를 찾을 수 없습니다.' });
      return res.status(200).json({ ok: true });
    } catch (err) {
      console.error('[news:id] delete error', err);
      return res.status(500).json({ ok: false, error: '기사를 삭제하지 못했습니다.' });
    }
  }

  res.setHeader('Allow', 'GET, PUT, DELETE');
  return res.status(405).json({ ok: false, error: 'Method not allowed' });
};
