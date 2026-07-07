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

  function renderList() {
    emptyState.classList.toggle('hidden', articles.length > 0);
    newsTableBody.innerHTML = articles.map(function (a) {
      return '<tr>' +
        '<td>' + escHtml(a.date) + '</td>' +
        '<td>' + escHtml(THEME_LABELS[a.theme] || a.theme) + '</td>' +
        '<td>' + escHtml(a.tagKo) + '</td>' +
        '<td class="title-cell">' + escHtml(a.titleKo) + '<span class="en">' + escHtml(a.titleEn) + '</span></td>' +
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

  function resetForm() {
    editorForm.reset();
    $('#fId').value = '';
    $('#fPublished').checked = true;
    editorError.textContent = '';
    deleteBtn.classList.add('hidden');
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
      $('#fTitleKo').value = article.titleKo;
      $('#fTitleEn').value = article.titleEn;
      $('#fBodyKo').value = (article.bodyKo || []).join('\n');
      $('#fBodyEn').value = (article.bodyEn || []).join('\n');
      $('#fPublished').checked = article.published !== false;
      deleteBtn.classList.remove('hidden');
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
      titleKo: $('#fTitleKo').value.trim(),
      titleEn: $('#fTitleEn').value.trim(),
      bodyKo: $('#fBodyKo').value.split('\n').map(function (s) { return s.trim(); }).filter(Boolean),
      bodyEn: $('#fBodyEn').value.split('\n').map(function (s) { return s.trim(); }).filter(Boolean),
      published: $('#fPublished').checked
    };
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
