/* Preserve the canonical SVG logo colours in browsers that apply a special
   dark-mode filter to small images/logos. The SVG remains the source artwork.
   Its paths are alpha masks, while their visible colour is painted as actual
   foreground text rather than background/image pixels. This matters on
   Samsung Internet, whose forced-dark engine can darken masked backgrounds. */
(function(){
  'use strict';

  var LOGO_SRC='/assets/dakhni-org-logo.svg';
  var SELECTOR='img.nav-mark,svg.nav-mark,canvas.nav-mark,img.seal-img,svg.seal-img,canvas.seal-img';

  function classNameOf(el){
    return (typeof el.className==='string') ? el.className : ((el.className&&el.className.baseVal)||'');
  }

  function makeMaskData(path, viewBox){
    var p=path.cloneNode(true);
    p.setAttribute('fill','#fff');
    p.removeAttribute('style');
    var svg=document.createElementNS('http://www.w3.org/2000/svg','svg');
    svg.setAttribute('xmlns','http://www.w3.org/2000/svg');
    svg.setAttribute('viewBox',viewBox);
    svg.appendChild(p);
    var text=new XMLSerializer().serializeToString(svg);
    return 'data:image/svg+xml;charset=utf-8,'+encodeURIComponent(text);
  }

  /* Fill a masked layer with foreground glyph pixels rather than a CSS
     background. Full-block glyphs deliberately overlap slightly so the
     resulting field is visually solid before the SVG alpha mask is applied. */
  function layer(maskUrl, colour, w, h){
    var s=document.createElement('span');
    s.setAttribute('aria-hidden','true');
    s.style.position='absolute';
    s.style.inset='0';
    s.style.display='block';
    s.style.overflow='hidden';
    s.style.pointerEvents='none';
    s.style.background='transparent';
    s.style.color=colour;
    s.style.webkitTextFillColor=colour;
    s.style.webkitMaskImage='url("'+maskUrl+'")';
    s.style.maskImage='url("'+maskUrl+'")';
    s.style.webkitMaskRepeat='no-repeat';
    s.style.maskRepeat='no-repeat';
    s.style.webkitMaskPosition='center';
    s.style.maskPosition='center';
    s.style.webkitMaskSize='contain';
    s.style.maskSize='contain';

    var ink=document.createElement('span');
    var cols=Math.max(10,Math.ceil(w/5)+6);
    var rows=Math.max(8,Math.ceil(h/8)+6);
    var line=new Array(cols+1).join('\u2588');
    ink.textContent=new Array(rows+1).join(line+'\n');
    ink.style.position='absolute';
    ink.style.left='-12px';
    ink.style.top='-12px';
    ink.style.whiteSpace='pre';
    ink.style.fontFamily='monospace';
    ink.style.fontSize='12px';
    ink.style.fontWeight='900';
    ink.style.lineHeight='8px';
    ink.style.letterSpacing='-2px';
    ink.style.color=colour;
    ink.style.webkitTextFillColor=colour;
    ink.style.userSelect='none';
    ink.style.webkitUserSelect='none';
    s.appendChild(ink);
    return s;
  }

  fetch(LOGO_SRC,{cache:'force-cache'})
    .then(function(r){ if(!r.ok) throw new Error('logo'); return r.text(); })
    .then(function(text){
      var doc=new DOMParser().parseFromString(text,'image/svg+xml');
      var svg=doc.documentElement;
      if(!svg || svg.nodeName.toLowerCase()!=='svg') return;
      var paths=svg.querySelectorAll('path');
      if(paths.length<2) return;
      var viewBox=svg.getAttribute('viewBox')||'0 0 1254 1254';
      var creamMask=makeMaskData(paths[0],viewBox);
      var brownMask=makeMaskData(paths[1],viewBox);

      function convert(el){
        if(!el || el.dataset && el.dataset.logoMask==='1') return;
        var cls=classNameOf(el);
        var rect=el.getBoundingClientRect();
        var cs=getComputedStyle(el);
        var w=Math.max(1,Math.round(rect.width||parseFloat(cs.width)||30));
        var h=Math.max(1,Math.round(rect.height||parseFloat(cs.height)||w));
        var alt=el.getAttribute('alt')||el.getAttribute('aria-label')||'';

        var wrap=document.createElement('span');
        wrap.className=cls;
        wrap.dataset.logoMask='1';
        wrap.style.position='relative';
        wrap.style.width=w+'px';
        wrap.style.height=h+'px';
        wrap.style.display='block';
        wrap.style.filter='none';
        wrap.style.mixBlendMode='normal';
        wrap.style.background='transparent';
        wrap.style.colorScheme='only light';
        if(alt){
          wrap.setAttribute('role','img');
          wrap.setAttribute('aria-label',alt);
        }else{
          wrap.setAttribute('aria-hidden','true');
        }

        wrap.appendChild(layer(creamMask,'#FAF7EF',w,h));
        wrap.appendChild(layer(brownMask,'#6B4710',w,h));
        el.replaceWith(wrap);
      }

      function scan(){
        document.querySelectorAll(SELECTOR).forEach(convert);
      }
      scan();
      /* The legacy logo normalizer in site.core.js is asynchronous. Re-scan
         briefly so this renderer wins any race without a permanent observer. */
      setTimeout(scan,120);
      setTimeout(scan,500);
      setTimeout(scan,1200);
    })
    .catch(function(){ /* Leave the existing SVG fallback untouched. */ });
})();
