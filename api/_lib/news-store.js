/* ============================================================
   News article storage — a single JSON array kept under one KV key.
   Traffic on a company newsroom is low and single-admin, so one
   read-modify-write per mutation is simpler than per-article keys or
   indexes and needs no locking.
   ============================================================ */
var kv = require('./kv');

var KEY = 'news:list';

// Admin picks a THEME instead of hand-authoring hex/gradient CSS — this
// mirrors tools/build_pages.py's BIZ palette so admin-authored articles
// look consistent with the affiliate pages linked from `biz`.
var THEMES = {
  culiver: { color: '#0E4E78', chipbg: 'rgba(14,78,120,.08)',
    overlay: 'linear-gradient(150deg,rgba(14,78,120,.32),rgba(10,44,70,.55))',
    cover: 'linear-gradient(150deg,rgba(14,78,120,.5),rgba(10,44,70,.7))',
    biz: 'culiver-aqua.html', labelKo: '컬리버', labelEn: 'CULIVER' },
  amp: { color: '#166578', chipbg: 'rgba(30,127,150,.09)',
    overlay: 'linear-gradient(150deg,rgba(30,127,150,.3),rgba(15,74,92,.55))',
    cover: 'linear-gradient(150deg,rgba(30,127,150,.5),rgba(15,74,92,.7))',
    biz: 'amp.html', labelKo: '에이엠피', labelEn: 'AMP' },
  cobaltive: { color: '#6E5D38', chipbg: 'rgba(142,122,92,.12)',
    overlay: 'linear-gradient(150deg,rgba(142,122,92,.3),rgba(94,79,58,.55))',
    cover: 'linear-gradient(150deg,rgba(142,122,92,.5),rgba(94,79,58,.7))',
    biz: 'cobaltive.html', labelKo: '코발티브', labelEn: 'COBALTIVE' },
  susinje: { color: '#3E7C4F', chipbg: 'rgba(62,124,79,.1)',
    overlay: 'linear-gradient(150deg,rgba(62,124,79,.3),rgba(36,82,50,.55))',
    cover: 'linear-gradient(150deg,rgba(62,124,79,.5),rgba(36,82,50,.7))',
    biz: 'susinje-farm.html', labelKo: '수신제팜', labelEn: 'SUSINJE FARM' },
  group: { color: '#0B2438', chipbg: 'rgba(11,36,56,.08)',
    overlay: 'linear-gradient(150deg,rgba(11,36,56,.34),rgba(8,24,38,.6))',
    cover: 'linear-gradient(150deg,rgba(11,36,56,.55),rgba(8,24,38,.75))',
    biz: null, labelKo: '컬리버 그룹', labelEn: 'CULIVER Group' }
};

var TAGS = {
  press: { ko: '보도자료', en: 'Press' },
  updates: { ko: '소식', en: 'Updates' },
  hiring: { ko: '채용', en: 'Hiring' }
};

// the 6 articles tools/build_pages.py originally baked in statically —
// seeded into KV on first read so the admin panel starts non-empty and
// can edit/delete them like any other article.
var SEED = [
  { id: 'news-1', theme: 'culiver', tag: 'press', date: '2026-06-01',
    titleKo: '컬리버, BFT 기반 흰다리새우 스마트 양식장 2호기 준공',
    titleEn: 'CULIVER completes second BFT-based smart shrimp farm',
    photo: 'news-1.jpg',
    bodyKo: ['컬리버가 BFT(바이오플락) 기반 흰다리새우 스마트 양식장 2호기를 준공했습니다. 이번 2호기는 데이터 기반 사육 관제 시스템을 전면 적용해 연중 안정 생산 역량을 한층 강화했습니다.',
      '육상 순환 양식 방식으로 항생제 없이 균일한 품질의 새우를 생산하며, 사육수는 계열사 에이엠피의 수처리 공정과 연계해 순환·재사용됩니다.',
      '컬리버 그룹은 이번 증설을 계기로 스마트 양식 생산 규모를 지속 확대해 나갈 계획입니다.'],
    bodyEn: ['CULIVER has completed its second BFT (biofloc technology) based smart shrimp farm. The new facility fully applies a data-driven husbandry control system, further strengthening year-round, stable production.',
      'The land-based recirculating method produces uniform-quality shrimp without antibiotics, with rearing water linked to affiliate AMP’s water-treatment process for reuse.',
      'CULIVER Group plans to keep expanding its smart-aquaculture production scale following this expansion.'] },
  { id: 'news-2', theme: 'cobaltive', tag: 'updates', date: '2026-05-01',
    titleKo: '코발티브, 굴패각 업사이클 소재 친환경 인증 획득',
    titleEn: 'COBALTIVE earns eco-certification for upcycled oyster-shell materials',
    photo: 'news-2.jpg',
    bodyKo: ['코발티브가 굴 패각을 업사이클한 친환경 소재로 인증을 획득했습니다. 버려지던 패각을 자원으로 되살려 폐기물과 배출을 구조적으로 줄이는 성과를 인정받았습니다.',
      '코발티브는 패각 정제·가공을 통해 탄산칼슘 기반 기능성 소재 ‘숨쉘’과 생활 제품 ‘셸픽’을 선보이고 있습니다.',
      '앞으로도 자원순환 소재 라인업을 확대해 나갈 예정입니다.'],
    bodyEn: ['COBALTIVE has earned certification for an eco-material upcycled from oyster shells. Turning discarded shells back into a resource was recognized for structurally cutting waste and emissions.',
      'Through shell refining and processing, COBALTIVE offers the calcium-carbonate-based functional material ‘SUMSHELL’ and the everyday product line ‘SHELLPICK’.',
      'The company plans to keep expanding its circular-materials lineup.'] },
  { id: 'news-3', theme: 'susinje', tag: 'updates', date: '2026-04-01',
    titleKo: '수신제팜, 데이터 기반 수경재배 채소 정기유통 시작',
    titleEn: 'SUSINJE FARM launches subscription delivery for hydroponic vegetables',
    photo: 'news-3.jpg',
    bodyKo: ['수신제팜이 데이터 기반 수경재배로 기른 채소의 정기유통을 시작했습니다. 스마트팜 환경제어로 균일한 품질을 유지하며, 산지에서 식탁까지 신선하게 배송합니다.',
      '순환수를 활용한 재배로 자원 효율을 높였으며, 가정과 기업 고객을 대상으로 정기배송 서비스를 운영합니다.'],
    bodyEn: ['SUSINJE FARM has launched subscription delivery for vegetables grown with data-driven hydroponics. Smart-farm environmental control keeps quality uniform, delivered fresh from farm to table.',
      'Growing with recirculated water improves resource efficiency, and the company runs recurring delivery for both household and business customers.'] },
  { id: 'news-4', theme: 'amp', tag: 'press', date: '2026-03-01',
    titleKo: '에이엠피, 산업용수 순환여과 플랜트 신규 수주',
    titleEn: 'AMP wins new industrial water recirculation plant contract',
    photo: 'news-4.jpg',
    bodyKo: ['에이엠피가 산업용수 순환여과 플랜트를 신규 수주했습니다. 순환여과(RAS)와 미생물 제제 기술을 결합해 용수 재이용률을 높이는 맞춤형 설비를 공급합니다.',
      '에이엠피는 양식 수처리에서 축적한 기술을 산업 현장으로 확장하며 수처리 사업 영역을 넓혀가고 있습니다.'],
    bodyEn: ['AMP has won a new contract for an industrial water recirculation plant, combining RAS and microbial-agent technology to deliver custom systems that raise water-reuse rates.',
      'AMP is expanding its water-treatment business into industrial sites, building on technology accumulated in aquaculture water treatment.'] },
  { id: 'news-5', theme: 'group', tag: 'hiring', date: '2026-02-01',
    titleKo: '컬리버 그룹 2026 상반기 신입·경력 공개채용 시작',
    titleEn: 'CULIVER Group opens 2026 first-half hiring',
    photo: 'news-5.jpg',
    bodyKo: ['컬리버 그룹이 2026년 상반기 신입·경력 공개채용을 시작합니다. 양식 생산, 수처리 엔지니어링, 소재 R&D, 스마트팜 재배 등 계열사 전 직무에서 인재를 모집합니다.',
      '자세한 직무 내용과 지원 방법은 채용 페이지에서 확인하실 수 있습니다.'],
    bodyEn: ['CULIVER Group is opening its 2026 first-half hiring for both new graduates and experienced professionals, recruiting across every affiliate role — aquaculture production, water-treatment engineering, materials R&D, and smart-farm cultivation.',
      'See the careers page for full role details and how to apply.'] },
  { id: 'news-6', theme: 'susinje', tag: 'updates', date: '2026-01-01',
    titleKo: '수신제팜 수경재배 채소, 대형 유통사 입점 확정',
    titleEn: 'SUSINJE FARM’s hydroponic vegetables land major retail placement',
    photo: 'news-6.jpg',
    bodyKo: ['수신제팜의 수경재배 채소가 대형 유통사 입점을 확정했습니다. 데이터 기반 재배로 균일한 품질을 확보한 점이 좋은 평가를 받았습니다.',
      '이번 입점을 통해 더 많은 소비자에게 신선한 채소를 선보일 수 있게 되었습니다.'],
    bodyEn: ['SUSINJE FARM’s hydroponic vegetables have secured placement with a major retailer, recognized for the uniform quality achieved through data-driven growing.',
      'The placement lets the company bring fresh vegetables to many more consumers.'] }
];

function withPublicFields(a) {
  var theme = THEMES[a.theme] || THEMES.group;
  var tag = TAGS[a.tag] || TAGS.updates;
  return {
    id: a.id,
    theme: a.theme,
    tag: a.tag,
    tagKo: tag.ko, tagEn: tag.en,
    date: a.date,
    titleKo: a.titleKo, titleEn: a.titleEn,
    bodyKo: a.bodyKo, bodyEn: a.bodyEn,
    photo: a.photo || null,
    color: theme.color, chipbg: theme.chipbg, overlay: theme.overlay, cover: theme.cover,
    biz: theme.biz,
    published: a.published !== false,
    createdAt: a.createdAt, updatedAt: a.updatedAt
  };
}

function seedRecord(s) {
  var now = 1750000000000; // fixed epoch for seed data; real writes stamp Date.now() at call time
  return Object.assign({ published: true, createdAt: now, updatedAt: now }, s);
}

async function loadAll() {
  var raw = await kv.kvGet(KEY);
  if (raw == null) {
    var seeded = SEED.map(seedRecord);
    await kv.kvSet(KEY, JSON.stringify(seeded));
    return seeded;
  }
  try {
    return JSON.parse(raw);
  } catch (e) {
    return [];
  }
}

async function saveAll(list) {
  await kv.kvSet(KEY, JSON.stringify(list));
}

function sortByDateDesc(list) {
  return list.slice().sort(function (a, b) { return a.date < b.date ? 1 : a.date > b.date ? -1 : 0; });
}

function slugify(titleKo, existingIds) {
  var base = 'news-' + Date.now().toString(36);
  var id = base, n = 1;
  while (existingIds.indexOf(id) !== -1) { id = base + '-' + n; n++; }
  return id;
}

async function list(opts) {
  opts = opts || {};
  var all = sortByDateDesc(await loadAll());
  var visible = opts.includeDrafts ? all : all.filter(function (a) { return a.published !== false; });
  var limited = typeof opts.limit === 'number' ? visible.slice(0, opts.limit) : visible;
  return limited.map(withPublicFields);
}

async function getWithNeighbors(id, opts) {
  opts = opts || {};
  var all = sortByDateDesc(await loadAll());
  var visible = opts.includeDrafts ? all : all.filter(function (a) { return a.published !== false; });
  var idx = visible.findIndex(function (a) { return a.id === id; });
  if (idx === -1) return null;
  return {
    article: withPublicFields(visible[idx]),
    prevId: idx < visible.length - 1 ? visible[idx + 1].id : null, // older
    nextId: idx > 0 ? visible[idx - 1].id : null // newer
  };
}

function validateInput(body) {
  var errors = [];
  if (!body || typeof body !== 'object') return ['Invalid payload'];
  if (!body.titleKo || !String(body.titleKo).trim()) errors.push('titleKo is required');
  if (!body.titleEn || !String(body.titleEn).trim()) errors.push('titleEn is required');
  if (!Array.isArray(body.bodyKo) || !body.bodyKo.length) errors.push('bodyKo must be a non-empty array');
  if (!Array.isArray(body.bodyEn) || !body.bodyEn.length) errors.push('bodyEn must be a non-empty array');
  if (!THEMES[body.theme]) errors.push('theme must be one of ' + Object.keys(THEMES).join(', '));
  if (!TAGS[body.tag]) errors.push('tag must be one of ' + Object.keys(TAGS).join(', '));
  if (!body.date || !/^\d{4}-\d{2}-\d{2}$/.test(body.date)) errors.push('date must be YYYY-MM-DD');
  return errors;
}

function sanitizeRecord(body) {
  return {
    theme: body.theme,
    tag: body.tag,
    date: body.date,
    titleKo: String(body.titleKo).trim().slice(0, 200),
    titleEn: String(body.titleEn).trim().slice(0, 200),
    bodyKo: body.bodyKo.map(function (p) { return String(p).trim(); }).filter(Boolean).slice(0, 40),
    bodyEn: body.bodyEn.map(function (p) { return String(p).trim(); }).filter(Boolean).slice(0, 40),
    photo: body.photo ? String(body.photo).trim().slice(0, 500) : null,
    published: body.published !== false
  };
}

async function create(body) {
  var errors = validateInput(body);
  if (errors.length) return { error: errors.join('; ') };
  var all = await loadAll();
  var now = Date.now();
  var record = Object.assign(
    { id: slugify(body.titleKo, all.map(function (a) { return a.id; })), createdAt: now, updatedAt: now },
    sanitizeRecord(body)
  );
  all.push(record);
  await saveAll(all);
  return { article: withPublicFields(record) };
}

async function update(id, body) {
  var errors = validateInput(body);
  if (errors.length) return { error: errors.join('; ') };
  var all = await loadAll();
  var idx = all.findIndex(function (a) { return a.id === id; });
  if (idx === -1) return { notFound: true };
  var record = Object.assign({}, all[idx], sanitizeRecord(body), { updatedAt: Date.now() });
  all[idx] = record;
  await saveAll(all);
  return { article: withPublicFields(record) };
}

async function remove(id) {
  var all = await loadAll();
  var next = all.filter(function (a) { return a.id !== id; });
  if (next.length === all.length) return { notFound: true };
  await saveAll(next);
  return { ok: true };
}

module.exports = {
  THEMES: THEMES, TAGS: TAGS,
  list: list, getWithNeighbors: getWithNeighbors,
  create: create, update: update, remove: remove
};
