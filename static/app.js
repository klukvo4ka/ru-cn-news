(function () {
  'use strict';

  const API      = '/api/news';
  const PER_PAGE = 20;

  const SOURCES = {
    'ТАСС':          { label: 'ТАСС',         cls: 'src-tass'    },
    'РИА Новости':   { label: 'РИА Новости',  cls: 'src-ria'     },
    'Синьхуа':       { label: 'Xinhua',        cls: 'src-xinhua'  },
    'Global Times':  { label: 'Global Times',  cls: 'src-gt'      },
  };

  const grid     = document.getElementById('news-grid');
  const sentinel = document.getElementById('sentinel');
  const spinner  = sentinel.querySelector('.spinner');
  const endMsg   = sentinel.querySelector('.end-msg');

  let lang    = '';
  let page    = 1;
  let loading = false;
  let done    = false;

  function esc(str) {
    return String(str ?? '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function stripTags(str) {
    return String(str ?? '').replace(/<[^>]+>/g, '').trim();
  }

  function fmtDate(str) {
    if (!str) return '';
    const d = new Date(str);
    if (isNaN(d.getTime())) return str.slice(0, 10);
    return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', year: 'numeric' });
  }

  function makeCard(a) {
    const src  = SOURCES[a.source] ?? { label: esc(a.source), cls: 'src-default' };
    const desc = stripTags(a.description);

    const card = document.createElement('article');
    card.className = 'card';
    card.innerHTML =
      '<div class="card-meta">' +
        '<span class="source-badge ' + src.cls + '">' + src.label + '</span>' +
        '<time>' + fmtDate(a.pub_date) + '</time>' +
      '</div>' +
      '<h2 class="card-title">' + esc(a.title) + '</h2>' +
      (desc ? '<p class="card-desc">' + esc(desc) + '</p>' : '') +
      '<a class="card-link" href="' + esc(a.link) + '" target="_blank" rel="noopener">читать →</a>';
    return card;
  }

  function showEmpty() {
    const el = document.createElement('div');
    el.className = 'empty-state';
    el.innerHTML = '<strong>Новостей нет</strong>Запустите scheduler для первой загрузки.';
    grid.appendChild(el);
  }

  async function loadPage() {
    if (loading || done) return;
    loading = true;
    spinner.hidden = false;
    endMsg.hidden  = true;

    const params = new URLSearchParams({ page });
    if (lang) params.set('lang', lang);

    try {
      const res  = await fetch(API + '?' + params);
      const data = await res.json();

      if (data.articles.length === 0 && page === 1) {
        showEmpty();
      } else {
        const frag = document.createDocumentFragment();
        data.articles.forEach(a => frag.appendChild(makeCard(a)));
        grid.appendChild(frag);
      }

      if (page >= data.pages) {
        done = true;
        observer.disconnect();
        if (data.total > 0) endMsg.hidden = false;
      } else {
        page++;
      }
    } catch (_) {
    } finally {
      loading = false;
      spinner.hidden = true;
    }
  }

  function reset(newLang) {
    lang    = newLang;
    page    = 1;
    loading = false;
    done    = false;
    grid.innerHTML = '';
    endMsg.hidden  = true;
    observer.observe(sentinel);
    loadPage();
  }

  const observer = new IntersectionObserver(
    entries => { if (entries[0].isIntersecting) loadPage(); },
    { rootMargin: '250px' }
  );

  document.querySelectorAll('.lang-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      if (btn.classList.contains('active')) return;
      document.querySelectorAll('.lang-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      reset(btn.dataset.lang);
    });
  });

  observer.observe(sentinel);
  loadPage();
}());
