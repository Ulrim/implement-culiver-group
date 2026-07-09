(function () {
  'use strict';

  var $ = function (sel, ctx) { return (ctx || document).querySelector(sel); };
  var $all = function (sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); };

  function escHtml(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  // capitalized lang codes match both the #fTitle{Lang}/#fBody{Lang} field
  // ids and the API's title{Lang}/body{Lang} JSON keys 1:1. Ko/En are
  // always the first two (required, matching api/_lib/news-store.js);
  // EXTRA_LANGS is derived rather than retyped so it can't drift out of
  // sync with ALL_LANGS.
  var ALL_LANGS = ['Ko', 'En', 'Vi', 'Th', 'Ja', 'Zh'];
  var EXTRA_LANGS = ALL_LANGS.slice(2);

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

  // matches availableArticleLangs() in assets/js/main.js: a language only
  // "counts" once both title AND body are filled in — a title-only or
  // body-only language isn't shown to any visitor either, so signaling it
  // as complete here would mislead the admin
  function langHasContent(a, lang) {
    return !!(a['title' + lang] && a['title' + lang].trim()) && !!(a['body' + lang] && a['body' + lang].length);
  }

  function extraLangCount(a) {
    return EXTRA_LANGS.filter(function (lang) { return langHasContent(a, lang); }).length;
  }

  function renderList() {
    emptyState.classList.toggle('hidden', articles.length > 0);
    newsTableBody.innerHTML = articles.map(function (a) {
      var extra = extraLangCount(a);
      return '<tr>' +
        '<td>' + escHtml(a.date) + '</td>' +
        '<td>' + escHtml(a.themeLabelKo || a.theme) + '</td>' +
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
  var PHOTO_HINT = 'jpg/png/webp/gif, 3MB 이하. 업로드하면 자동으로 리사이즈되어 JPG로 저장됩니다.';

  /* ---- language tabs ---- */
  var LANG_TAB_NAMES = { Ko: '한국어', En: 'English', Vi: 'Tiếng Việt', Th: 'ภาษาไทย', Ja: '日本語', Zh: '中文' };

  function setupLangTabs() {
    var tabs = $all('.lang-tab');
    var panels = $all('.lang-panel');
    tabs.forEach(function (tab) {
      tab.addEventListener('click', function () { activateLangTab(tab.getAttribute('data-lang')); });
    });
    ALL_LANGS.forEach(function (lang) {
      var title = $('#fTitle' + lang), body = $('#fBody' + lang);
      if (title) title.addEventListener('input', updateTabIndicators);
      if (body) body.addEventListener('input', updateTabIndicators);
    });
  }

  // a language only "has content" once BOTH title and body are filled —
  // matches availableArticleLangs() in assets/js/main.js, which is what
  // actually decides whether a visitor can pick this language at all
  function updateTabIndicators() {
    ALL_LANGS.forEach(function (lang) {
      var title = $('#fTitle' + lang), body = $('#fBody' + lang);
      var hasContent = !!(title && title.value.trim()) && !!(body && body.value.trim());
      var tab = $('.lang-tab[data-lang="' + lang + '"]');
      if (!tab) return;
      tab.classList.toggle('has-content', hasContent);
      // the has-content dot is decorative (CSS ::after) — fold the same
      // information into aria-label so screen-reader users get it too
      tab.setAttribute('aria-label', LANG_TAB_NAMES[lang] + (hasContent ? ' (작성됨)' : ''));
    });
  }

  function activateLangTab(lang) {
    $all('.lang-tab').forEach(function (t) {
      var active = t.getAttribute('data-lang') === lang;
      t.classList.toggle('active', active);
      t.setAttribute('aria-pressed', active ? 'true' : 'false');
    });
    $all('.lang-panel').forEach(function (p) { p.classList.toggle('hidden', p.getAttribute('data-lang') !== lang); });
  }

  setupLangTabs();

  /* ---- photo upload ---- */
  function setPhotoPreview(url) {
    if (url) {
      photoPreview.style.backgroundImage = "url('" + url + "')";
      photoPreview.innerHTML = '';
      photoPreview.setAttribute('aria-label', '업로드된 대표 이미지 미리보기');
    } else {
      photoPreview.style.backgroundImage = '';
      photoPreview.innerHTML = '<span class="ph-empty" aria-hidden="true">이미지 없음</span>';
      photoPreview.setAttribute('aria-label', '이미지 없음');
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

  var photoUploadSeq = 0; // guards against a slower earlier upload's response clobbering a later one

  fPhotoFile.addEventListener('change', function () {
    var file = fPhotoFile.files && fPhotoFile.files[0];
    if (!file) return;
    if (!/^image\/(jpeg|png|webp|gif)$/.test(file.type)) {
      photoStatus.textContent = 'jpg, png, webp, gif 이미지만 업로드할 수 있습니다.';
      fPhotoFile.value = '';
      return;
    }
    var mySeq = ++photoUploadSeq;
    photoStatus.textContent = '업로드 중...';
    resizeImageToJpeg(file, 1600, 0.85)
      .then(function (jpegBlob) { return blobToBase64(jpegBlob); })
      .then(function (base64) {
        return api('/api/admin/upload', { method: 'POST', body: { contentType: 'image/jpeg', dataBase64: base64 } });
      })
      .then(function (res) {
        if (mySeq !== photoUploadSeq) return; // superseded by a later file selection
        if (!res.ok || !res.data.ok) {
          photoStatus.textContent = (res.data && res.data.error) || '업로드에 실패했습니다.';
          return;
        }
        fPhoto.value = res.data.url;
        setPhotoPreview(res.data.url);
        photoStatus.textContent = '업로드 완료.';
      })
      .catch(function () {
        if (mySeq !== photoUploadSeq) return;
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

  var REQUIRED_ADMIN_LANGS = ['Ko', 'En'];
  var REQUIRED_LANG_NAMES = { Ko: '한국어', En: '영어' };

  editorForm.addEventListener('submit', function (e) {
    e.preventDefault();
    editorError.textContent = '';

    // required-language check by hand: the HTML `required` attribute
    // can't be relied on here because #fTitleEn/#fBodyEn (and any other
    // language's fields) live inside a .lang-panel that's display:none
    // while that tab isn't active, and browsers silently exempt hidden
    // fields from constraint validation — Save would otherwise post
    // nothing and show no error at all if the admin never opens the
    // English tab
    var missingLang = REQUIRED_ADMIN_LANGS.filter(function (lang) {
      var title = $('#fTitle' + lang), body = $('#fBody' + lang);
      return !(title && title.value.trim()) || !(body && body.value.trim());
    })[0];
    if (missingLang) {
      activateLangTab(missingLang);
      editorError.textContent = REQUIRED_LANG_NAMES[missingLang] + ' 제목과 본문을 입력해 주세요.';
      return;
    }

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
