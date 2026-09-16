/* Render the canonical SVG logo through canvas so browser force-dark image
   heuristics cannot recolour its pixels. The source asset remains SVG. */
(function(){
  'use strict';

  var LOGO_SRC='/assets/dakhni-org-logo.svg';
  var SELECTOR='img.nav-mark,svg.nav-mark,img.seal-img,svg.seal-img';
  var busy=new WeakSet();

  function classNameOf(el){
    return (typeof el.className==='string') ? el.className : ((el.className&&el.className.baseVal)||'');
  }

  function convert(el){
    if(!el || el.tagName.toLowerCase()==='canvas' || busy.has(el)) return;
    busy.add(el);

    var rect=el.getBoundingClientRect();
    var computed=window.getComputedStyle(el);
    var cssW=Math.max(1,Math.round(rect.width||parseFloat(computed.width)||30));
    var cssH=Math.max(1,Math.round(rect.height||parseFloat(computed.height)||cssW));
    var dpr=Math.min(window.devicePixelRatio||1,4);
    var canvas=document.createElement('canvas');
    canvas.className=classNameOf(el);
    canvas.width=Math.round(cssW*dpr);
    canvas.height=Math.round(cssH*dpr);
    canvas.style.width=cssW+'px';
    canvas.style.height=cssH+'px';
    canvas.style.display='block';
    canvas.style.filter='none';
    canvas.style.mixBlendMode='normal';

    var alt=el.getAttribute('alt')||el.getAttribute('aria-label')||'';
    if(alt){
      canvas.setAttribute('role','img');
      canvas.setAttribute('aria-label',alt);
    }else{
      canvas.setAttribute('aria-hidden','true');
    }

    var image=new Image();
    image.decoding='async';
    image.onload=function(){
      var ctx=canvas.getContext('2d',{alpha:true});
      if(!ctx) return;
      ctx.setTransform(dpr,0,0,dpr,0,0);
      ctx.clearRect(0,0,cssW,cssH);
      ctx.drawImage(image,0,0,cssW,cssH);
      if(el.isConnected){
        el.replaceWith(canvas);
      }else{
        // Another logo normalisation step may have replaced the node while
        // this image was decoding. Re-scan so the final connected node is
        // still converted to the canvas surface.
        scan();
      }
    };
    image.src=LOGO_SRC;
  }

  function scan(){
    document.querySelectorAll(SELECTOR).forEach(convert);
  }

  scan();
  // site.js previously normalised the same logo asynchronously; these
  // follow-up scans deliberately win that race without a permanent observer.
  setTimeout(scan,120);
  setTimeout(scan,500);
  setTimeout(scan,1200);
})();
