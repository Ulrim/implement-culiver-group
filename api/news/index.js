/* ============================================================
   GET  /api/news         — public: published articles (?limit=N)
   GET  /api/news?all=1   — admin only: includes drafts
   POST /api/news         — admin only: create an article
   ============================================================ */
var auth = require('../_lib/auth');
var store = require('../_lib/news-store');

module.exports = async function handler(req, res) {
  if (req.method === 'GET') {
    var authed = auth.isAuthed(req);
    var wantAll = req.query.all === '1' && authed;
    var limit = req.query.limit ? parseInt(req.query.limit, 10) : undefined;
    try {
      var items = await store.list({ includeDrafts: wantAll, limit: limit });
      return res.status(200).json({ ok: true, items: items });
    } catch (err) {
      console.error('[news] list error', err);
      return res.status(500).json({ ok: false, error: '뉴스 목록을 불러오지 못했습니다.' });
    }
  }

  if (req.method === 'POST') {
    if (!auth.isAuthed(req)) {
      return res.status(401).json({ ok: false, error: '로그인이 필요합니다.' });
    }
    var body = req.body;
    if (typeof body === 'string') {
      try { body = JSON.parse(body); } catch (e) { body = {}; }
    }
    try {
      var result = await store.create(body || {});
      if (result.error) return res.status(400).json({ ok: false, error: result.error });
      return res.status(201).json({ ok: true, article: result.article });
    } catch (err) {
      console.error('[news] create error', err);
      return res.status(500).json({ ok: false, error: '기사를 저장하지 못했습니다.' });
    }
  }

  res.setHeader('Allow', 'GET, POST');
  return res.status(405).json({ ok: false, error: 'Method not allowed' });
};
