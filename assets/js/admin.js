(function () {
  'use strict';

  var $ = function (sel, ctx) { return (ctx || document).querySelector(sel); };
  var $all = function (sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); };

  function escHtml(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  var THEME_LABELS = {
    culiver: '컬리버', amp: '에이엠피', cobaltive: '코발티브', susinje: '수신제팜', group: '그룹'
  };

  // capitalized lang codes match both the #fTitle{Lang}/#fBody{Lang} field
  // ids and the API's title{Lang}/body{Lang} JSON keys 1:1
  var ALL_LANGS = ['Ko', 'En', 'Vi', 'Th', 'Ja', 'Zh'];
  var EXTRA_LANGS = ['Vi', 'Th', 'Ja', 'Zh'];

  var loginView = $('#loginView'), listView = $('#listView'), editorView = $('#editorView');
  var logoutBtn = $('#logoutBtn');
  var newsTableBody = $('#newsTableBody'), emptyState = $('#emptyState');
  var toastEl = $('#toast');
  var articles = []; // cache of the last-loaded admin list, keyed by id below

  function showToast(msg) {
    toastEl.textContent = msg;
    toastEl.classList.add('show');
    setTimeout(function () { toastEl.classList.remove('show'); }, 2200);
  }

  function setView(view) {
    [loginView, listView, editorView].forEach(function (v) { v.classList.add('hidden'); });
    view.classList.remove('hidden');
    logoutBtn.classList.toggle('hidden', view === loginView);
  }

  function api(path, opts) {
    opts = opts || {};
    return fetch(path, {
      method: opts.method || 'GET',
      headers: opts.body ? { 'Content-Type': 'application/json' } : undefined,
      body: opts.body ? JSON.stringify(opts.body) : undefined
    }).then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (data) {
        return { ok: r.ok, status: r.status, data: data };
      });
    });
  }

  /* ---------------------------------------------- login */
  $('#loginForm').addEventListener('submit', function (e) {
    e.preventDefault();
    var password = $('#loginPassword').value;
    var errorEl = $('#loginError');
    var btn = $('#loginSubmit');
    errorEl.textContent = '';
    btn.disabled = true;
    api('/api/admin/login', { method: 'POST', body: { password: password } }).then(function (res) {
      btn.disabled = false;
      if (!res.ok || !res.data.ok) {
        errorEl.textContent = (res.data && res.data.error) || '로그인에 실패했습니다.';
        return;
      }
      $('#loginPassword').value = '';
      setView(listView);
      loadList();
    }).catch(function () {
      btn.disabled = false;
      errorEl.textContent = '네트워크 오류입니다. 잠시 후 다시 시도해 주세요.';
    });
  });

  logoutBtn.addEventListener('click', function () {
    api('/api/admin/logout', { method: 'POST' }).then(function () { setView(loginView); });
  });

  /* ---------------------------------------------- list */
  function statusPill(published) {
    return published
      ? '<span class="status-pill pub">게시됨</span>'
      : '<span class="status-pill draft">임시저장</span>';
  }

  function extraLangCount(a) {
    return EXTRA_LANGS.filter(function (lang) {
      return (a['title' + lang] && a['title' + lang].trim()) || (a['body' + lang] && a['body' + lang].length);
    }).length;
  }

  function renderList() {
    emptyState.classList.toggle('hidden', articles.length > 0);
    newsTableBody.innerHTML = articles.map(function (a) {
      var extra = extraLangCount(a);
      return '<tr>' +
        '<td>' + escHtml(a.date) + '</td>' +
        '<td>' + escHtml(THEME_LABELS[a.theme] || a.theme) + '</td>' +
        '<td>' + escHtml(a.tagKo) + '</td>' +
        '<td class="title-cell">' + escHtml(a.titleKo) + '<span class="en">' + escHtml(a.titleEn) +
        (extra ? ' · +' + extra + '개 언어' : '') + '</span></td>' +
        '<td>' + statusPill(a.published) + '</td>' +
        '<td class="row-actions">' +
        '<button class="btn btn-line" data-edit="' + escHtml(a.id) + '">수정</button>' +
        '<button class="btn btn-danger" data-delete="' + escHtml(a.id) + '">삭제</button>' +
        '</td></tr>';
    }).join('');
  }

  function loadList() {
    api('/api/news?all=1').then(function (res) {
      if (!res.ok || !res.data.ok) { showToast('목록을 불러오지 못했습니다.'); return; }
      articles = res.data.items;
      renderList();
    });
  }

  newsTableBody.addEventListener('click', function (e) {
    var editId = e.target.getAttribute('data-edit');
    var delId = e.target.getAttribute('data-delete');
    if (editId) { openEditor(articles.filter(function (a) { return a.id === editId; })[0]); }
    if (delId) {
      if (!window.confirm('이 글을 삭제하시겠습니까? 되돌릴 수 없습니다.')) return;
      api('/api/news/' + encodeURIComponent(delId), { method: 'DELETE' }).then(function (res) {
        if (!res.ok || !res.data.ok) { showToast((res.data && res.data.error) || '삭제하지 못했습니다.'); return; }
        showToast('삭제했습니다.');
        loadList();
      });
    }
  });

  /* ---------------------------------------------- editor */
  var editorForm = $('#editorForm'), editorError = $('#editorError'), deleteBtn = $('#deleteBtn');
  var fPhotoFile = $('#fPhotoFile'), fPhoto = $('#fPhoto'), photoPreview = $('#photoPreview'), photoStatus = $('#photoStatus');
  var PHOTO_HINT = 'jpg/png/webp/gif, 4MB 이하. 업로드하면 자동으로 리사이즈되어 JPG로 저장됩니다.';

  /* ---- language tabs ---- */
  function setupLangTabs() {
    var tabs = $all('.lang-tab');
    var panels = $all('.lang-panel');
    tabs.forEach(function (tab) {
      tab.addEventListener('click', function () {
        var lang = tab.getAttribute('data-lang');
        tabs.forEach(function (t) { t.classList.toggle('active', t === tab); });
        panels.forEach(function (p) { p.classList.toggle('hidden', p.getAttribute('data-lang') !== lang); });
      });
    });
    ALL_LANGS.forEach(function (lang) {
      var title = $('#fTitle' + lang), body = $('#fBody' + lang);
      if (title) title.addEventListener('input', updateTabIndicators);
      if (body) body.addEventListener('input', updateTabIndicators);
    });
  }

  function updateTabIndicators() {
    ALL_LANGS.forEach(function (lang) {
      var title = $('#fTitle' + lang), body = $('#fBody' + lang);
      var hasContent = !!(title && title.value.trim()) || !!(body && body.value.trim());
      var tab = $('.lang-tab[data-lang="' + lang + '"]');
      if (tab) tab.classList.toggle('has-content', hasContent);
    });
  }

  function activateLangTab(lang) {
    $all('.lang-tab').forEach(function (t) { t.classList.toggle('active', t.getAttribute('data-lang') === lang); });
    $all('.lang-panel').forEach(function (p) { p.classList.toggle('hidden', p.getAttribute('data-lang') !== lang); });
  }

  setupLangTabs();

  /* ---- photo upload ---- */
  function setPhotoPreview(url) {
    if (url) {
      photoPreview.style.backgroundImage = "url('" + url + "')";
      photoPreview.innerHTML = '';
    } else {
      photoPreview.style.backgroundImage = '';
      photoPreview.innerHTML = '<span class="ph-empty">이미지 없음</span>';
    }
  }

  function resizeImageToJpeg(file, maxDim, quality) {
    return new Promise(function (resolve, reject) {
      var objectUrl = URL.createObjectURL(file);
      var img = new Image();
      img.onload = function () {
        URL.revokeObjectURL(objectUrl);
        var scale = Math.min(1, maxDim / Math.max(img.naturalWidth, img.naturalHeight));
        var w = Math.max(1, Math.round(img.naturalWidth * scale));
        var h = Math.max(1, Math.round(img.naturalHeight * scale));
        var canvas = document.createElement('canvas');
        canvas.width = w; canvas.height = h;
        var ctx = canvas.getContext('2d');
        ctx.fillStyle = '#fff'; // flatten transparency (PNG/GIF -> opaque JPEG) onto white, not black
        ctx.fillRect(0, 0, w, h);
        ctx.drawImage(img, 0, 0, w, h);
        canvas.toBlob(function (blob) {
          if (!blob) { reject(new Error('resize failed')); return; }
          resolve(blob);
        }, 'image/jpeg', quality);
      };
      img.onerror = function () { URL.revokeObjectURL(objectUrl); reject(new Error('이미지를 읽을 수 없습니다.')); };
      img.src = objectUrl;
    });
  }

  function blobToBase64(blob) {
    return new Promise(function (resolve, reject) {
      var reader = new FileReader();
      reader.onload = function () { resolve(String(reader.result).split(',')[1] || ''); };
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  }

  fPhotoFile.addEventListener('change', function () {
    var file = fPhotoFile.files && fPhotoFile.files[0];
    if (!file) return;
    if (!/^image\/(jpeg|png|webp|gif)$/.test(file.type)) {
      photoStatus.textContent = 'jpg, png, webp, gif 이미지만 업로드할 수 있습니다.';
      fPhotoFile.value = '';
      return;
    }
    photoStatus.textContent = '업로드 중...';
    resizeImageToJpeg(file, 1600, 0.85)
      .then(function (jpegBlob) { return blobToBase64(jpegBlob); })
      .then(function (base64) {
        return api('/api/admin/upload', { method: 'POST', body: { contentType: 'image/jpeg', dataBase64: base64 } });
      })
      .then(function (res) {
        if (!res.ok || !res.data.ok) {
          photoStatus.textContent = (res.data && res.data.error) || '업로드에 실패했습니다.';
          return;
        }
        fPhoto.value = res.data.url;
        setPhotoPreview(res.data.url);
        photoStatus.textContent = '업로드 완료.';
      })
      .catch(function () {
        photoStatus.textContent = '업로드 중 오류가 발생했습니다.';
      })
      .then(function () { fPhotoFile.value = ''; });
  });

  fPhoto.addEventListener('blur', function () { setPhotoPreview(fPhoto.value.trim()); });

  function resetForm() {
    editorForm.reset();
    $('#fId').value = '';
    $('#fPublished').checked = true;
    editorError.textContent = '';
    deleteBtn.classList.add('hidden');
    setPhotoPreview('');
    photoStatus.textContent = PHOTO_HINT;
    activateLangTab('Ko');
    updateTabIndicators();
  }

  function openEditor(article) {
    resetForm();
    $('#editorTitle').textContent = article ? '글 수정' : '새 글 작성';
    if (article) {
      $('#fId').value = article.id;
      $('#fTheme').value = article.theme;
      $('#fTag').value = article.tag;
      $('#fDate').value = article.date;
      $('#fPhoto').value = article.photo || '';
      setPhotoPreview(article.photo || '');
      ALL_LANGS.forEach(function (lang) {
        var title = $('#fTitle' + lang), body = $('#fBody' + lang);
        if (title) title.value = article['title' + lang] || '';
        if (body) body.value = (article['body' + lang] || []).join('\n');
      });
      $('#fPublished').checked = article.published !== false;
      deleteBtn.classList.remove('hidden');
      updateTabIndicators();
    }
    setView(editorView);
  }

  $('#newBtn').addEventListener('click', function () { openEditor(null); });
  $('#cancelEditBtn').addEventListener('click', function () { setView(listView); });

  deleteBtn.addEventListener('click', function () {
    var id = $('#fId').value;
    if (!id) return;
    if (!window.confirm('이 글을 삭제하시겠습니까? 되돌릴 수 없습니다.')) return;
    api('/api/news/' + encodeURIComponent(id), { method: 'DELETE' }).then(function (res) {
      if (!res.ok || !res.data.ok) { showToast((res.data && res.data.error) || '삭제하지 못했습니다.'); return; }
      showToast('삭제했습니다.');
      setView(listView);
      loadList();
    });
  });

  editorForm.addEventListener('submit', function (e) {
    e.preventDefault();
    var id = $('#fId').value;
    var payload = {
      theme: $('#fTheme').value,
      tag: $('#fTag').value,
      date: $('#fDate').value,
      photo: $('#fPhoto').value.trim() || null,
      published: $('#fPublished').checked
    };
    ALL_LANGS.forEach(function (lang) {
      var title = $('#fTitle' + lang), body = $('#fBody' + lang);
      payload['title' + lang] = title ? title.value.trim() : '';
      payload['body' + lang] = body ? body.value.split('\n').map(function (s) { return s.trim(); }).filter(Boolean) : [];
    });
    editorError.textContent = '';
    var saveBtn = $('#saveBtn');
    saveBtn.disabled = true;
    var req = id
      ? api('/api/news/' + encodeURIComponent(id), { method: 'PUT', body: payload })
      : api('/api/news', { method: 'POST', body: payload });
    req.then(function (res) {
      saveBtn.disabled = false;
      if (!res.ok || !res.data.ok) {
        editorError.textContent = (res.data && res.data.error) || '저장하지 못했습니다.';
        return;
      }
      showToast(id ? '수정했습니다.' : '작성했습니다.');
      setView(listView);
      loadList();
    }).catch(function () {
      saveBtn.disabled = false;
      editorError.textContent = '네트워크 오류입니다. 잠시 후 다시 시도해 주세요.';
    });
  });

  /* ---------------------------------------------- init */
  api('/api/admin/me').then(function (res) {
    if (res.ok && res.data.authed) {
      setView(listView);
      loadList();
    } else {
      setView(loginView);
    }
  }).catch(function () { setView(loginView); });
})();
