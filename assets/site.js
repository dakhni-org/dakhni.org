/* dakhni.org — shared scripts (generated) */

/* ---- */
(function(){
  var root = document.documentElement;
  root.classList.add('js');               // content is visible by default; .js enables the reveal animation
  try { var y = document.getElementById('year'); if (y) y.textContent = new Date().getFullYear(); } catch (e) {}
  var els = document.querySelectorAll('.reveal, .reveal-left, .reveal-right');
  try {
    var obs = new IntersectionObserver(function(entries){
      entries.forEach(function(e, i){
        if (e.isIntersecting) { setTimeout(function(){ e.target.classList.add('visible'); }, i * 80); obs.unobserve(e.target); }
      });
    }, { threshold: 0, rootMargin: '0px 0px -8% 0px' });
    els.forEach(function(el){ obs.observe(el); });
  } catch (e) {
    // IntersectionObserver unavailable — just show everything
    els.forEach(function(el){ el.classList.add('visible'); });
  }
  var tog = document.querySelector('.nav-toggle');
  var links = document.querySelector('.nav-links');
  if (tog && links) {
    tog.addEventListener('click', function(){
      var open = links.classList.toggle('open');
      tog.setAttribute('aria-expanded', open ? 'true' : 'false');
      document.body.classList.toggle('menu-open', open);
    });
    links.querySelectorAll('a').forEach(function(a){
      a.addEventListener('click', function(){
        links.classList.remove('open');
        tog.setAttribute('aria-expanded', 'false');
        document.body.classList.remove('menu-open');
      });
    });
  }
})();

/* ---- */
(function(){
  var el = document.getElementById('ai-disclosure');
  if (!el) return;
  var closeBtn = document.getElementById('disclosure-close');
  var acceptBtn = document.getElementById('disclosure-accept');
  var shown = false;
  var lastFocused = null;
  function focusable() {
    // Both buttons are always present and visible together whenever the
    // dialog is open, so no visibility check is needed here — and
    // offsetParent (a common visibility check) is always null for
    // position:fixed elements like .disclosure-close, which would
    // otherwise wrongly filter it out.
    return [closeBtn, acceptBtn].filter(Boolean);
  }
  function show() {
    if (shown || localStorage.getItem('dakhni_disclosure_seen')) return;
    shown = true;
    lastFocused = document.activeElement;
    el.classList.add('open');
    document.body.style.overflow = 'hidden';
    closeBtn.focus();
  }
  function dismiss() {
    localStorage.setItem('dakhni_disclosure_seen', '1');
    el.classList.remove('open');
    document.body.style.overflow = '';
    if (lastFocused && typeof lastFocused.focus === 'function') lastFocused.focus();
    lastFocused = null;
  }
  acceptBtn.addEventListener('click', dismiss);
  closeBtn.addEventListener('click', dismiss);
  el.querySelector('.disclosure-backdrop').addEventListener('click', dismiss);
  document.addEventListener('keydown', function(e){
    if (!el.classList.contains('open')) return;
    if (e.key === 'Escape') { e.stopImmediatePropagation(); dismiss(); return; }
    if (e.key !== 'Tab') return;
    // Trap focus inside the dialog while it's open.
    var items = focusable();
    if (!items.length) return;
    var first = items[0], last = items[items.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  });
  setTimeout(show, 3000);
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
    btn.focus();
  }
  btn.addEventListener('click',openSearch);
  input.addEventListener('input',render);
  modal.addEventListener('click',function(e){if(e.target.hasAttribute('data-close'))closeSearch();});
  list.addEventListener('click',function(e){if(e.target.closest('a'))closeSearch();});
  document.addEventListener('keydown',function(e){
    if(modal.hidden) return;
    if(e.key==='Escape'){closeSearch();return;}
    if(e.key!=='Tab') return;
    // Trap focus inside the dialog while it's open -- the result list is
    // rebuilt on every keystroke, so the focusable set is recomputed fresh
    // each time rather than cached.
    var items=modal.querySelectorAll('input, button, a[href]');
    if(!items.length) return;
    var first=items[0], last=items[items.length-1];
    if(e.shiftKey && document.activeElement===first){e.preventDefault();last.focus();}
    else if(!e.shiftKey && document.activeElement===last){e.preventDefault();first.focus();}
  });
})();

