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

/* ---- Dakhni Heritage Quiz ---- */
var DAKHNI_QUIZ = [
  /* DYNASTIES */
  {q:"Which dynasty founded the city of Hyderabad in 1591?",opts:["Bahmani Sultanate","Adil Shahi Dynasty","Qutb Shahi Dynasty","Asaf Jahi Nizams"],ans:"Qutb Shahi Dynasty",t:"Dynasties"},
  {q:"Who founded the Bahmani Sultanate in 1347?",opts:["Ahmad Shah I","Alauddin Bahman Shah","Mahmud Gawan","Sultan Quli Qutb Shah"],ans:"Alauddin Bahman Shah",t:"Dynasties"},
  {q:"The Gol Gumbaz in Bijapur was built by which dynasty?",opts:["Qutb Shahi","Bahmani","Adil Shahi","Asaf Jahi"],ans:"Adil Shahi",t:"Dynasties"},
  {q:"Which Bahmani vizier built the famous madrasa at Bidar in 1472?",opts:["Yusuf Adil Shah","Mahmud Gawan","Sultan Quli","Qasim Barid I"],ans:"Mahmud Gawan",t:"Dynasties"},
  {q:"The Battle of Talikota (1565) united the Deccan sultanates against which empire?",opts:["Mughal Empire","Delhi Sultanate","Vijayanagara Empire","Maratha Confederacy"],ans:"Vijayanagara Empire",t:"Dynasties"},
  {q:"Which sultan composed the Kitab-i-Nauras, a treatise on music and the nine ragas?",opts:["Muhammad Quli Qutb Shah","Ahmad Shah Bahmani","Ibrahim Adil Shah II","Mir Osman Ali Khan"],ans:"Ibrahim Adil Shah II",t:"Dynasties"},
  {q:"In which year did Hyderabad State accede to the Indian Union (Operation Polo)?",opts:["1946","1947","1948","1950"],ans:"1948",t:"Dynasties"},
  {q:"Who was the last and seventh Nizam of Hyderabad?",opts:["Mir Qamar-ud-Din Khan","Nasir-ud-Dawlah","Afzal-ud-Dawlah","Mir Osman Ali Khan"],ans:"Mir Osman Ali Khan",t:"Dynasties"},
  {q:"The Qutb Shahi dynasty ruled primarily from which fort?",opts:["Daulatabad Fort","Bidar Fort","Golconda Fort","Gulbarga Fort"],ans:"Golconda Fort",t:"Dynasties"},
  {q:"Which city replaced Gulbarga as the Bahmani capital in 1424?",opts:["Bijapur","Bidar","Warangal","Aurangabad"],ans:"Bidar",t:"Dynasties"},
  {q:"The founder of the Asaf Jahi dynasty is best known by which Mughal title?",opts:["Wazir-ul-Mamalik","Nizam-ul-Mulk","Sipahsalar","Subedar-i-Deccan"],ans:"Nizam-ul-Mulk",t:"Dynasties"},
  {q:"How many sultans ruled the Bahmani Sultanate over its 180-year history?",opts:["Twelve","Fifteen","Eighteen","Twenty-two"],ans:"Eighteen",t:"Dynasties"},
  /* CITIES */
  {q:"Hyderabad was founded on the banks of which river?",opts:["Krishna","Godavari","Musi","Tungabhadra"],ans:"Musi",t:"Cities"},
  {q:"The Thousand Pillar Temple (Rudresvara) is located in which Deccan city?",opts:["Bidar","Gulbarga","Bijapur","Warangal"],ans:"Warangal",t:"Cities"},
  {q:"Which city served as the first capital of the Bahmani Sultanate?",opts:["Bidar","Gulbarga (Kalaburagi)","Warangal","Daulatabad"],ans:"Gulbarga (Kalaburagi)",t:"Cities"},
  {q:"The Ibrahim Rauza mausoleum in Bijapur is often compared to which monument, which it predated?",opts:["Red Fort","Taj Mahal","Humayun's Tomb","Fatehpur Sikri"],ans:"Taj Mahal",t:"Cities"},
  {q:"Bidriware — the black-metal craft — originated in which Deccan city?",opts:["Bijapur","Hyderabad","Warangal","Bidar"],ans:"Bidar",t:"Cities"},
  {q:"Which city is near the Ajanta and Ellora cave temples?",opts:["Bidar","Raichur","Aurangabad","Nizamabad"],ans:"Aurangabad",t:"Cities"},
  {q:"Nanded houses Hazur Sahib, the takht associated with which Sikh Guru?",opts:["Guru Nanak Dev","Guru Tegh Bahadur","Guru Gobind Singh","Guru Harkrishan"],ans:"Guru Gobind Singh",t:"Cities"},
  {q:"Golconda Fort stands just west of which modern Indian city?",opts:["Bijapur","Aurangabad","Hyderabad","Warangal"],ans:"Hyderabad",t:"Cities"},
  {q:"Raichur is historically significant as the site of repeated battles between the Deccan sultanates and which rival power?",opts:["Delhi Sultanate","Vijayanagara Empire","Mughal Empire","Maratha Confederacy"],ans:"Vijayanagara Empire",t:"Cities"},
  /* SUFISM */
  {q:"Which Sufi saint established the first major khanqah in the Deccan at Khuldabad (c. 1327)?",opts:["Bandanawaz Gisudaraz","Burhanuddin Gharib","Shah Sharfuddin Maneri","Shah Hussain Wali"],ans:"Burhanuddin Gharib",t:"Sufism"},
  {q:"Hazrat Bandanawaz Gisudaraz (d. 1422) is buried in which city?",opts:["Hyderabad","Bidar","Gulbarga","Aurangabad"],ans:"Gulbarga",t:"Sufism"},
  {q:"Bandanawaz Gisudaraz belonged to which Sufi order?",opts:["Qadiri","Suhrawardi","Naqshbandi","Chishti"],ans:"Chishti",t:"Sufism"},
  {q:"Shah Hussain Wali's major dargah is located in which city?",opts:["Aurangabad","Gulbarga","Nanded","Bidar"],ans:"Nanded",t:"Sufism"},
  {q:"What does 'urs' mean in the Sufi dargah tradition?",opts:["Morning prayer gathering","Annual death-anniversary commemoration","Weekly qawwali session","Monthly charity feast"],ans:"Annual death-anniversary commemoration",t:"Sufism"},
  {q:"The twin dargah of Maula Ali and Yousuf (Yousufain Sharif) is in which city?",opts:["Bijapur","Gulbarga","Hyderabad","Aurangabad"],ans:"Hyderabad",t:"Sufism"},
  {q:"Burhanuddin Gharib journeyed to the Deccan as a disciple of which Chishti master in Delhi?",opts:["Nizamuddin Auliya","Fariduddin Ganjshakar","Qutbuddin Bakhtiyar Kaki","Moinuddin Chishti"],ans:"Nizamuddin Auliya",t:"Sufism"},
  {q:"The saint known as 'Shah Khamosh' (the Silent Saint) is associated with which Deccan city?",opts:["Bidar","Gulbarga","Hyderabad","Aurangabad"],ans:"Aurangabad",t:"Sufism"},
  {q:"What does 'silsila' mean in the Sufi tradition?",opts:["A Friday gathering of disciples","The chain of teachers from the Prophet","A collection of devotional poems","The garden of a dargah"],ans:"The chain of teachers from the Prophet",t:"Sufism"},
  /* CUISINE */
  {q:"What cooking technique is the hallmark of Hyderabadi kachchi biryani?",opts:["Tandoor roasting","Dum pukht (slow steam cooking)","Deep frying","Open-flame grilling"],ans:"Dum pukht (slow steam cooking)",t:"Cuisine"},
  {q:"Haleem in Hyderabad is traditionally associated with which religious occasion?",opts:["Eid al-Fitr","Diwali","Muharram","Ugadi"],ans:"Muharram",t:"Cuisine"},
  {q:"What is 'lukhmi' — the distinctive Hyderabadi snack?",opts:["A sweet rice pudding","A flat bread baked in tandoor","A square flaky pastry with minced meat filling","A lentil soup with fried onions"],ans:"A square flaky pastry with minced meat filling",t:"Cuisine"},
  {q:"What is 'qubani ka meetha'?",opts:["A vermicelli pudding with rose water","A dessert made from dried apricots","A halwa made from wheat and ghee","A custard made from coconut milk"],ans:"A dessert made from dried apricots",t:"Cuisine"},
  {q:"What does 'dum pukht' literally mean in Persian?",opts:["Slow fire","Cooked under steam","Sealed pot","Long simmered"],ans:"Cooked under steam",t:"Cuisine"},
  {q:"The 'kachchi' technique in Hyderabadi biryani means the meat is:",opts:["Pre-cooked before layering with rice","Raw marinated, layered with rice, and slow-cooked together","Deep fried before mixing","Boiled separately from the rice"],ans:"Raw marinated, layered with rice, and slow-cooked together",t:"Cuisine"},
  /* ARCHITECTURE */
  {q:"The Charminar in Hyderabad was built in which year?",opts:["1565","1591","1624","1687"],ans:"1591",t:"Architecture"},
  {q:"How many minarets does the Charminar have?",opts:["Two","Four","Six","Eight"],ans:"Four",t:"Architecture"},
  {q:"Approximately how wide is the main dome of the Gol Gumbaz at Bijapur?",opts:["28 metres","35 metres","44 metres","56 metres"],ans:"44 metres",t:"Architecture"},
  {q:"The Gulbarga Fort Jama Masjid (1367) is architecturally unusual among South Asian mosques because:",opts:["It has the tallest minarets in the Deccan","Its entire prayer hall is covered with small domes — no open courtyard","It was built entirely without arches","Its qibla faces east rather than west"],ans:"Its entire prayer hall is covered with small domes — no open courtyard",t:"Architecture"},
  {q:"Construction of the Mecca Masjid in Hyderabad began in 1614 and was completed in 1694 — spanning roughly:",opts:["40 years","60 years","80 years","100 years"],ans:"80 years",t:"Architecture"},
  {q:"Which feature is most distinctive of Deccani Islamic architecture compared to Mughal style?",opts:["Red sandstone with white marble inlay","Bulbous domes with lotus-medallion stucco decoration","Multi-storey minarets with balcony tiers","Flat roofs with arched colonnades"],ans:"Bulbous domes with lotus-medallion stucco decoration",t:"Architecture"},
  {q:"The Ibrahim Rauza mausoleum in Bijapur was built for which Adil Shahi sultan?",opts:["Yusuf Adil Shah","Ibrahim Adil Shah II","Muhammad Adil Shah","Ali Adil Shah II"],ans:"Ibrahim Adil Shah II",t:"Architecture"},
  /* LANGUAGE */
  {q:"The Dakhni dialect developed from which linguistic base brought south by Bahmani armies?",opts:["Braj Bhasha","Awadhi","Khari Boli","Maithili"],ans:"Khari Boli",t:"Language"},
  {q:"Who is widely regarded as the 'Father of Urdu Poetry'?",opts:["Muhammad Quli Qutb Shah","Wali Deccani (Wali Aurangabadi)","Ibrahim Adil Shah II","Mir Taqi Mir"],ans:"Wali Deccani (Wali Aurangabadi)",t:"Language"},
  {q:"What does 'hau' mean in the Dakhni dialect?",opts:["No","Come here","Yes","Why"],ans:"Yes",t:"Language"},
  {q:"What does 'nakko' mean in the Dakhni dialect?",opts:["Quickly","No / don't","Later","Good morning"],ans:"No / don't",t:"Language"},
  {q:"What does 'kaiku' mean in Dakhni?",opts:["Who","When","Why","Where"],ans:"Why",t:"Language"},
  {q:"Muhammad Quli Qutb Shah's divan is estimated to be approximately how many verses long?",opts:["10,000 verses","25,000 verses","50,000 verses","80,000 verses"],ans:"50,000 verses",t:"Language"},
  {q:"Which Sufi saint of Gulbarga wrote early devotional prose in Dakhni, helping establish it as a literary language?",opts:["Burhanuddin Gharib","Bandanawaz Gisudaraz","Shah Khamosh","Shah Hussain Wali"],ans:"Bandanawaz Gisudaraz",t:"Language"},
  {q:"What is a 'divan' in classical Urdu/Persian literature?",opts:["A royal council chamber","A collected body of poetry arranged by rhyme","A type of musical recitation","A commentary on the Quran"],ans:"A collected body of poetry arranged by rhyme",t:"Language"},
  /* MUSIC */
  {q:"Qawwali devotional music is most closely associated with which Sufi order?",opts:["Naqshbandi","Qadiri","Chishti","Suhrawardi"],ans:"Chishti",t:"Music"},
  {q:"What is a 'marsiya' in the Dakhni/Urdu literary tradition?",opts:["A love poem praising the beloved","An elegy commemorating Imam Hussain's martyrdom","A qawwali sung at a saint's urs","A ghazal composed for a royal patron"],ans:"An elegy commemorating Imam Hussain's martyrdom",t:"Music"},
  {q:"The Kitab-i-Nauras is primarily a treatise on:",opts:["Astronomy and mathematics","Nine ragas and their cultural associations","Sufi meditation practices","The history of the Adil Shahi court"],ans:"Nine ragas and their cultural associations",t:"Music"},
  {q:"The annual Muharram commemorations in Hyderabad mark the martyrdom of which figure?",opts:["Imam Ali","Imam Hussain","Imam Hassan","Hazrat Abbas"],ans:"Imam Hussain",t:"Music"},
  /* CRAFTS */
  {q:"Paithani silk weaving is traditionally associated with which town near Aurangabad?",opts:["Paithan (Prathisthana)","Osmanabad","Latur","Nanded"],ans:"Paithan (Prathisthana)",t:"Crafts"},
  {q:"Himroo — a silk-cotton brocade — is woven in which city?",opts:["Hyderabad","Bidar","Aurangabad","Bijapur"],ans:"Aurangabad",t:"Crafts"},
  {q:"Kalamkari is a traditional craft involving which technique?",opts:["Silver inlay on black metal","Hand-painted or block-printed cotton textiles","Silk weaving with gold thread borders","Lacquerware with floral motifs"],ans:"Hand-painted or block-printed cotton textiles",t:"Crafts"},
  {q:"For roughly how many centuries has Bidriware been produced in Bidar using the same technique?",opts:["Two centuries","Three centuries","Five centuries","Eight centuries"],ans:"Five centuries",t:"Crafts"},
  {q:"Bidriware is an alloy primarily of which metal, darkened with ammonium chloride?",opts:["Copper","Iron","Zinc","Bronze"],ans:"Zinc",t:"Crafts"},
  /* HERITAGE & SACRED SITES */
  {q:"The Mecca Masjid in Hyderabad is named after bricks in its arch allegedly containing soil from:",opts:["Medina","Jerusalem","Mecca","Karbala"],ans:"Mecca",t:"Heritage"},
  {q:"The Ramappa Temple (Rudresvara) near Warangal was inscribed as a UNESCO World Heritage Site in:",opts:["2004","2013","2017","2021"],ans:"2021",t:"Heritage"},
  {q:"What does 'tehzeeb' mean in Hyderabadi culture?",opts:["A sweet delicacy made during Eid","The ethos of refinement, courtesy and polished speech","A form of Sufi music","A type of embroidery on bridal garments"],ans:"The ethos of refinement, courtesy and polished speech",t:"Heritage"},
  {q:"The annual Bonalu festival in Hyderabad is dedicated to which goddess?",opts:["Saraswati","Lakshmi","Mahakali (Mahankali)","Parvati"],ans:"Mahakali (Mahankali)",t:"Heritage"},
  {q:"Bathukamma is a floral festival celebrated primarily by which community in Telangana?",opts:["Muslim women of old Hyderabad","Telugu Hindu women","Marathi-speaking women of Marathwada","Sikh women of Nanded"],ans:"Telugu Hindu women",t:"Heritage"},
  {q:"Osmania University — notable as an early university to use an Indian language as its medium of instruction — was founded in:",opts:["1902","1910","1918","1925"],ans:"1918",t:"Heritage"},
  {q:"What is a 'khanqah' in the Sufi tradition?",opts:["A Sufi hospice where disciples live, worship and receive visitors","The grave and shrine of a Sufi saint","A weekly gathering for recitation of poetry","A document certifying a student to teach"],ans:"A Sufi hospice where disciples live, worship and receive visitors",t:"Heritage"},
  {q:"The Salar Jung Museum in Hyderabad houses one of Asia's finest private collections, assembled by:",opts:["Mahmud Gawan","Salar Jung I (Mir Turab Ali Khan)","Nawab Imad ul-Mulk","Afzal-ud-Dawlah"],ans:"Salar Jung I (Mir Turab Ali Khan)",t:"Heritage"}
];

(function () {
  function shuffled(a) {
    var arr = a.slice(), i = arr.length, j, t;
    while (i) { j = Math.floor(Math.random() * i--); t = arr[i]; arr[i] = arr[j]; arr[j] = t; }
    return arr;
  }
  function el(id) { return document.getElementById(id); }

  var questions, current, score;

  function startQuiz() {
    questions = shuffled(DAKHNI_QUIZ).slice(0, 10);
    current = 0; score = 0;
    el('quiz-intro').hidden = true;
    el('quiz-result').hidden = true;
    el('quiz-stage').hidden = false;
    showQuestion();
  }

  function showQuestion() {
    var q = questions[current];
    el('quiz-fill').style.width = Math.round((current / 10) * 100) + '%';
    el('quiz-label').textContent = 'Question ' + (current + 1) + ' of 10';
    el('quiz-q').textContent = q.q;
    var opts = shuffled(q.opts);
    var container = el('quiz-opts');
    container.innerHTML = '';
    opts.forEach(function (opt) {
      var btn = document.createElement('button');
      btn.className = 'quiz-opt';
      btn.textContent = opt;
      btn.addEventListener('click', function () { handleAnswer(btn, q.ans); });
      container.appendChild(btn);
    });
    el('quiz-next').hidden = true;
  }

  function handleAnswer(btn, correctAns) {
    var btns = el('quiz-opts').querySelectorAll('.quiz-opt');
    btns.forEach(function (b) {
      b.disabled = true;
      if (b.textContent === correctAns) b.classList.add('correct');
      else if (b === btn) b.classList.add('wrong');
    });
    if (btn.textContent === correctAns) score++;
    el('quiz-next').hidden = false;
  }

  function nextQuestion() {
    current++;
    if (current >= 10) { showResult(); } else { showQuestion(); }
  }

  function showResult() {
    el('quiz-stage').hidden = true;
    var wrong = 10 - score;
    el('quiz-score-num').textContent = score;
    el('quiz-score-breakdown').textContent = score + ' correct · ' + wrong + ' incorrect';
    var tiers = [
      [0,2,'The Deccan awaits you — time to explore deeper.'],
      [3,4,'A curious visitor. The sultanates have much more to offer.'],
      [5,6,'Solid knowledge. You know your Deccan well.'],
      [7,8,'The Deccan runs through your veins.'],
      [9,9,'A near-perfect score — a true Dakhni scholar.'],
      [10,10,'Ek dum Dakhni! Perfect score. The Deccan is your home.']
    ];
    var comment = '';
    for (var i = 0; i < tiers.length; i++) {
      if (score >= tiers[i][0] && score <= tiers[i][1]) { comment = tiers[i][2]; break; }
    }
    el('quiz-score-comment').textContent = comment;
    el('quiz-result').hidden = false;
  }

  function init() {
    if (!el('quiz-start')) return;
    el('quiz-start').addEventListener('click', startQuiz);
    el('quiz-replay').addEventListener('click', startQuiz);
    el('quiz-next').addEventListener('click', nextQuestion);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else { init(); }
})();
