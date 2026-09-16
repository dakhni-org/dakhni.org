/* dakhni.org — shared script loader */
(function(){
  function load(src){
    return new Promise(function(resolve,reject){
      var s=document.createElement('script');
      s.src=src;
      s.async=false;
      s.onload=resolve;
      s.onerror=reject;
      document.head.appendChild(s);
    });
  }
  load('/assets/site.core.js').then(function(){
    return load('/assets/logo-canvas.js');
  }).catch(function(){
    /* Keep the page usable even if an auxiliary script is unavailable. */
  });
})();
