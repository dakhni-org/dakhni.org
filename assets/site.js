/* dakhni.org — shared scripts (generated) */

/* ---- */
document.getElementById('year').textContent = new Date().getFullYear();
  const obs = new IntersectionObserver(entries => {
    entries.forEach((e, i) => {
      if (e.isIntersecting) setTimeout(() => e.target.classList.add('visible'), i * 80);
    });
  }, { threshold: 0.08 });
  document.querySelectorAll('.reveal').forEach(el => obs.observe(el));
  (function(){
    var tog = document.querySelector('.nav-toggle');
    var links = document.querySelector('.nav-links');
    if(!tog || !links) return;
    tog.addEventListener('click', function(){
      var open = links.classList.toggle('open');
      tog.setAttribute('aria-expanded', open ? 'true' : 'false');
      document.body.classList.toggle('menu-open', open);
    });
  })();

/* ---- */
(function(){
  var el = document.getElementById('ai-disclosure');
  if (!el) return;
  if (!localStorage.getItem('dakhni_disclosure_seen')) {
    el.classList.add('open');
    document.body.style.overflow = 'hidden';
  }
  function dismiss() {
    localStorage.setItem('dakhni_disclosure_seen', '1');
    el.classList.remove('open');
    document.body.style.overflow = '';
  }
  document.getElementById('disclosure-accept').addEventListener('click', dismiss);
  el.querySelector('.disclosure-backdrop').addEventListener('click', dismiss);
})();

/* ---- */
(function(){
  var path = window.location.pathname.replace(/\/index\.html$/, '/');
  if (path === '') path = '/';
  // mark the top-level section
  var sections = [
    ['/heritage/',  'a[href="/heritage/"]'],
    ['/dynasties/', 'a[href="/dynasties/"]'],
    ['/language/',  'a[href="/language/"]'],
    ['/sufism/',    'a[href="/sufism/"]'],
    ['/cities/',    'a[href="/cities/"]'],
    ['/landmarks/', 'a[href="/landmarks/"]'],
    ['/sacred-sites/', 'a[href="/sacred-sites/"]'],
    ['/',           'a[href="/"]']
  ];
  for (var i = 0; i < sections.length; i++) {
    var prefix = sections[i][0];
    if (path === prefix || (prefix !== '/' && path.indexOf(prefix) === 0)) {
      var link = document.querySelector('.nav-links ' + sections[i][1]);
      if (link) link.setAttribute('aria-current', 'page');
      break;
    }
  }
  // mark the deeper sub-item if any
  var sub = document.querySelector('.dropdown a[href="' + path + '"]');
  if (sub) sub.setAttribute('aria-current', 'page');
})();

/* ---- */
(function(){
  var btn=document.querySelector('.nav-search-btn');
  var modal=document.getElementById('ds-search');
  if(!btn||!modal) return;
  var input=document.getElementById('ds-search-input');
  var list=document.getElementById('ds-search-results');
  var hint=document.getElementById('ds-search-hint');
  var data=null,loading=false;
  function esc(s){return String(s).replace(/[&<>"]/g,function(c){return ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'})[c];});}
  function reEsc(s){return s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');}
  function hl(text,terms){var safe=terms.map(reEsc).filter(Boolean);if(!safe.length)return esc(text);var re=new RegExp('('+safe.join('|')+')','gi');var out='',last=0,m;while((m=re.exec(text))!==null){out+=esc(text.slice(last,m.index))+'<mark>'+esc(m[0])+'</mark>';last=m.index+m[0].length;if(m.index===re.lastIndex)re.lastIndex++;}return out+esc(text.slice(last));}
  function snippet(p,terms){var pos=-1,text=p.b||'',lb=p._b||'',i,k;for(i=0;i<terms.length;i++){k=lb.indexOf(terms[i]);if(k>-1&&(pos<0||k<pos))pos=k;}if(pos<0){text=p.d||'';var ld=text.toLowerCase();for(i=0;i<terms.length;i++){k=ld.indexOf(terms[i]);if(k>-1&&(pos<0||k<pos))pos=k;}if(pos<0)return hl(text.slice(0,160),terms);}var start=pos>60?pos-60:0,end=pos+120;var frag=text.slice(start,end);if(start>0)frag='\u2026 '+frag;if(end<text.length)frag=frag+' \u2026';return hl(frag,terms);}
  function load(){
    if(data||loading) return;
    loading=true;
    fetch('/assets/search-index.json').then(function(r){return r.json();}).then(function(d){data=d;for(var i=0;i<d.length;i++){d[i]._h=(d[i].t+' '+d[i].s+' '+d[i].d+' '+(d[i].b||'')).toLowerCase();d[i]._b=(d[i].b||'').toLowerCase();}if(!modal.hidden)render();}).catch(function(){hint.textContent='Search is unavailable right now.';});
  }
  function render(){
    var q=input.value.trim().toLowerCase();
    if(!q){list.innerHTML='';hint.hidden=false;return;}
    hint.hidden=true;
    if(!data){list.innerHTML='<li class="ds-search-msg">Loading…</li>';return;}
    var terms=q.split(/\s+/);
    var hits=data.filter(function(p){
      return terms.every(function(t){return p._h.indexOf(t)>-1;});
    }).slice(0,12);
    if(!hits.length){list.innerHTML='<li class="ds-search-msg">No results for “'+esc(q)+'”.</li>';return;}
    list.innerHTML=hits.map(function(p){
      return '<li role="option"><a href="'+esc(p.u)+'"><span class="ds-r-title">'+hl(p.t,terms)+'</span><span class="ds-r-sec">'+esc(p.s)+'</span><span class="ds-r-desc">'+snippet(p,terms)+'</span></a></li>';
    }).join('');
  }
  function openSearch(){
    modal.hidden=false;
    document.body.classList.add('ds-search-open');
    btn.setAttribute('aria-expanded','true');
    load();
    setTimeout(function(){input.focus();},30);
  }
  function closeSearch(){
    modal.hidden=true;
    document.body.classList.remove('ds-search-open');
    btn.setAttribute('aria-expanded','false');
  }
  btn.addEventListener('click',openSearch);
  input.addEventListener('input',render);
  modal.addEventListener('click',function(e){if(e.target.hasAttribute('data-close'))closeSearch();});
  list.addEventListener('click',function(e){if(e.target.closest('a'))closeSearch();});
  document.addEventListener('keydown',function(e){if(e.key==='Escape'&&!modal.hidden)closeSearch();});
})();
