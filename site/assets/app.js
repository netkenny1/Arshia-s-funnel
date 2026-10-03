/* Guest list form: posts to a configured endpoint (Google Apps Script / Formspree / your own API).
   If no endpoint is configured, it falls back to opening WhatsApp with the message pre-filled,
   so the funnel works on day one with zero backend. */
(function () {
  var cfg = window.ARSHIA || {};
  var form = document.getElementById('guestlist-form');
  var status = document.getElementById('form-status');
  var waDirect = document.getElementById('wa-direct');

  function waLink(text) {
    var num = (cfg.whatsapp || '').replace(/\D/g, '');
    var base = num ? 'https://wa.me/' + num : 'https://wa.me/';
    return base + '?text=' + encodeURIComponent(text);
  }

  if (waDirect) {
    waDirect.href = waLink('Hey Arshia, guest list please. Name: / IG: / Date: / Group size: ');
    if (!cfg.whatsapp) waDirect.textContent = 'WhatsApp (number not set yet)';
  }

  // UTM + referrer capture so you can see which TikTok / IG post actually filled the list
  var params = new URLSearchParams(location.search);
  var attribution = {
    utm_source: params.get('utm_source') || '',
    utm_medium: params.get('utm_medium') || '',
    utm_campaign: params.get('utm_campaign') || '',
    utm_content: params.get('utm_content') || '',
    referrer: document.referrer || '',
    landing: location.pathname
  };
  try {
    var first = localStorage.getItem('arshia_first_touch');
    if (!first) localStorage.setItem('arshia_first_touch', JSON.stringify(attribution));
    else attribution.first_touch = JSON.parse(first);
  } catch (e) {}

  if (!form) return;

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    status.className = 'status';
    var fd = new FormData(form);
    if (fd.get('_hp')) return; // honeypot
    var data = {
      name: (fd.get('name') || '').trim(),
      instagram: (fd.get('instagram') || '').trim().replace(/^@/, ''),
      phone: (fd.get('phone') || '').trim(),
      event: fd.get('event') || '',
      party_size: fd.get('party_size') || '1',
      consent: !!fd.get('consent'),
      submitted_at: new Date().toISOString(),
      attribution: attribution
    };
    if (!data.name || !data.instagram || !data.phone || !data.event || !data.consent) {
      status.textContent = 'Fill in every field and tick the box.';
      status.className = 'status err';
      return;
    }

    var msg = 'Guest list please.\nName: ' + data.name + '\nIG: @' + data.instagram +
              '\nDate: ' + data.event + '\nGroup: ' + data.party_size;

    if (!cfg.endpoint) {
      status.textContent = 'Opening WhatsApp…';
      status.className = 'status ok';
      window.open(waLink(msg), '_blank');
      return;
    }

    status.textContent = 'Sending…';
    fetch(cfg.endpoint, {
      method: 'POST',
      mode: 'no-cors', // Apps Script redirects; we treat a non-throwing fetch as success
      headers: { 'Content-Type': 'text/plain;charset=utf-8' },
      body: JSON.stringify(data)
    }).then(function () {
      status.textContent = "You're on the list. We'll confirm on WhatsApp before the night.";
      status.className = 'status ok';
      form.reset();
    }).catch(function () {
      status.textContent = 'Something broke. Sending you to WhatsApp instead…';
      status.className = 'status err';
      window.open(waLink(msg), '_blank');
    });
  });
})();
