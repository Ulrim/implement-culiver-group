/* ============================================================
   Image upload — wraps @vercel/blob's put(). Falls back to a data:
   URI when BLOB_READ_WRITE_TOKEN is unset (no real Blob store linked
   yet), the same "keep local/dev testable without real credentials"
   pattern as api/_lib/kv.js. The fallback is NOT for production use —
   it bloats the article's KV payload and skips the CDN entirely.
   ============================================================ */

function blobConfigured() {
  return !!process.env.BLOB_READ_WRITE_TOKEN;
}

async function uploadImage(pathname, buffer, contentType) {
  if (!blobConfigured()) {
    return { url: 'data:' + contentType + ';base64,' + buffer.toString('base64') };
  }
  var { put } = require('@vercel/blob');
  var result = await put(pathname, buffer, {
    access: 'public',
    contentType: contentType,
    addRandomSuffix: true
  });
  return { url: result.url };
}

module.exports = { uploadImage: uploadImage, blobConfigured: blobConfigured };
