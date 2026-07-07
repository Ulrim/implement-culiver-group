/* ============================================================
   POST /api/contact — 문의 폼 처리 (Vercel Serverless Function)

   환경 변수 (Vercel → Project → Settings → Environment Variables):
     RESEND_API_KEY     Resend API 키 (필수)              re_xxx
     CONTACT_TO_EMAIL   문의를 받을 주소 (필수)           you@culiver.co.kr
     CONTACT_FROM_EMAIL 발신 주소 (선택, 도메인 인증 필요)
                        미설정 시 onboarding@resend.dev (테스트용)

   외부 npm 패키지 없이 Resend REST API를 fetch로 호출합니다.
   ============================================================ */

const MAX = { name: 100, email: 200, company: 120, type: 40, message: 4000 };
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function clean(v, max) {
  return typeof v === 'string' ? v.trim().slice(0, max) : '';
}
function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, function (c) {
    return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
  });
}

module.exports = async function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ ok: false, error: 'Method not allowed' });
  }

  // parse body (Vercel usually parses JSON into req.body; guard for string)
  var body = req.body;
  if (typeof body === 'string') {
    try { body = JSON.parse(body); } catch (e) { body = {}; }
  }
  body = body || {};

  // honeypot: bots fill hidden field → silently accept, do nothing
  if (clean(body._gotcha, 200)) {
    return res.status(200).json({ ok: true });
  }

  var name = clean(body.name, MAX.name);
  var email = clean(body.email, MAX.email);
  var company = clean(body.company, MAX.company);
  var type = clean(body.type, MAX.type);
  var message = clean(body.message, MAX.message);

  if (!name || !email || !message) {
    return res.status(400).json({ ok: false, error: '이름, 이메일, 문의 내용을 입력해 주세요.' });
  }
  if (!EMAIL_RE.test(email)) {
    return res.status(400).json({ ok: false, error: '올바른 이메일 주소를 입력해 주세요.' });
  }

  var apiKey = process.env.RESEND_API_KEY;
  var to = process.env.CONTACT_TO_EMAIL;
  var from = process.env.CONTACT_FROM_EMAIL || 'CULIVER GROUP <onboarding@resend.dev>';

  if (!apiKey || !to) {
    console.error('[contact] Missing RESEND_API_KEY or CONTACT_TO_EMAIL env var');
    return res.status(500).json({ ok: false, error: '서버 설정 오류로 전송하지 못했습니다. 잠시 후 다시 시도해 주세요.' });
  }

  var subject = '[컬리버 그룹 문의] ' + (type || '일반') + ' · ' + name;
  var lines = [
    ['이름', name],
    ['이메일', email],
    ['회사·소속', company || '-'],
    ['문의 유형', type || '-'],
    ['내용', message]
  ];
  var html = '<h2 style="font-family:sans-serif">새 문의가 접수되었습니다</h2>' +
    '<table style="font-family:sans-serif;font-size:14px;border-collapse:collapse">' +
    lines.map(function (l) {
      return '<tr><td style="padding:6px 14px 6px 0;color:#666;vertical-align:top;white-space:nowrap">' +
        escapeHtml(l[0]) + '</td><td style="padding:6px 0;white-space:pre-wrap">' +
        escapeHtml(l[1]) + '</td></tr>';
    }).join('') + '</table>';
  var text = lines.map(function (l) { return l[0] + ': ' + l[1]; }).join('\n');

  try {
    var payload = { from: from, to: [to], subject: subject, html: html, text: text, reply_to: email };
    var r = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + apiKey,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });
    if (!r.ok) {
      var detail = await r.text();
      console.error('[contact] Resend error', r.status, detail);
      return res.status(502).json({ ok: false, error: '메일 전송에 실패했습니다. 잠시 후 다시 시도해 주세요.' });
    }
    return res.status(200).json({ ok: true });
  } catch (err) {
    console.error('[contact] Unexpected error', err);
    return res.status(500).json({ ok: false, error: '전송 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.' });
  }
};
