var auth = require('../_lib/auth');

module.exports = async function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ ok: false, error: 'Method not allowed' });
  }
  res.setHeader('Set-Cookie', auth.clearSessionCookie(req));
  return res.status(200).json({ ok: true });
};
