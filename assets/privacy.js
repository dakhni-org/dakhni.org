/* Optional analytics and comments load only after a visitor chooses them. */
(function () {
  'use strict';
  var key = 'dakhni-analytics-consent';
  var banner = document.getElementById('cookie-choice');
  var analyticsLoaded = false;

  function choice() {
    try { return localStorage.getItem(key); } catch (e) { return null; }
  }
  function loadAnalytics() {
    if (analyticsLoaded) return;
    analyticsLoaded = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', 'G-N9RETSEPQ9');
    var script = document.createElement('script');
    script.async = true;
    script.src = 'https://www.googletagmanager.com/gtag/js?id=G-N9RETSEPQ9';
    document.head.appendChild(script);
  }
  if (choice() === 'accepted') loadAnalytics();
  else if (choice() !== 'rejected' && banner) banner.hidden = false;

  document.querySelectorAll('[data-analytics]').forEach(function (button) {
    button.addEventListener('click', function () {
      var accepted = button.dataset.analytics === 'accept';
      try { localStorage.setItem(key, accepted ? 'accepted' : 'rejected'); } catch (e) {}
      if (banner) banner.hidden = true;
      if (accepted) loadAnalytics();
      else if (analyticsLoaded && window.gtag) {
        window['ga-disable-G-N9RETSEPQ9'] = true;
        window.gtag('consent', 'update', { analytics_storage: 'denied' });
        // Remove the already loaded tag and its listeners by reloading with rejection saved.
        window.location.reload();
      }
    });
  });
  document.querySelectorAll('[data-privacy-settings]').forEach(function (button) {
    button.addEventListener('click', function () {
      if (banner) { banner.hidden = false; banner.querySelector('button').focus(); }
    });
  });

  var commentsButton = document.querySelector('.comments-load');
  if (commentsButton) commentsButton.addEventListener('click', function () {
    commentsButton.disabled = true;
    commentsButton.textContent = 'Loading comments…';
    var pageUrl = commentsButton.dataset.disqusUrl;
    var pageId = commentsButton.dataset.disqusId;
    window.disqus_config = function () {
      this.page.url = pageUrl;
      this.page.identifier = pageId;
    };
    var script = document.createElement('script');
    script.src = 'https://' + commentsButton.dataset.disqusShortname + '.disqus.com/embed.js';
    script.async = true;
    script.onerror = function () {
      commentsButton.disabled = false;
      commentsButton.textContent = 'Try loading comments again';
    };
    document.head.appendChild(script);
  });
})();
