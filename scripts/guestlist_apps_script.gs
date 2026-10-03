/**
 * Google Apps Script backend for the guest list form. Free, no server, lands in a Google Sheet
 * Arshia can open on his phone at the door.
 *
 * SETUP (5 minutes):
 *  1. Create a Google Sheet called "arshia.wav guest list". Add a tab named "list".
 *  2. Extensions -> Apps Script. Paste this file. Save.
 *  3. Deploy -> New deployment -> Type: Web app. Execute as: Me. Who has access: Anyone.
 *  4. Copy the Web app URL into data/artist.json -> "guestlist_endpoint". Rebuild / push.
 *  5. Optional: set WHATSAPP_WEBHOOK to a WhatsApp Cloud API or Make/Zapier webhook to auto-confirm.
 *
 * Columns written: timestamp, name, instagram, phone, event, party_size, consent, utm_source, utm_medium,
 * utm_campaign, utm_content, referrer, landing, first_touch (json), status
 */
var SHEET_NAME = 'list';
var WHATSAPP_WEBHOOK = ''; // optional

function doPost(e) {
  var data = {};
  try { data = JSON.parse(e.postData.contents); } catch (err) { return out({ ok: false, error: 'bad json' }); }
  if (!data.name || !data.instagram || !data.phone) return out({ ok: false, error: 'missing fields' });

  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(SHEET_NAME) || ss.insertSheet(SHEET_NAME);
  if (sh.getLastRow() === 0) {
    sh.appendRow(['timestamp', 'name', 'instagram', 'phone', 'event', 'party_size', 'consent',
                  'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'referrer', 'landing', 'first_touch', 'status']);
  }
  var a = data.attribution || {};
  // de-dupe: same instagram + same event = update, not a new row
  var rows = sh.getDataRange().getValues();
  var ig = String(data.instagram).toLowerCase().replace(/^@/, '');
  for (var i = 1; i < rows.length; i++) {
    if (String(rows[i][2]).toLowerCase() === ig && rows[i][4] === data.event) {
      sh.getRange(i + 1, 6).setValue(data.party_size);
      sh.getRange(i + 1, 1).setValue(new Date());
      return out({ ok: true, updated: true });
    }
  }
  sh.appendRow([new Date(), data.name, ig, normalizePhone(data.phone), data.event, data.party_size, data.consent ? 'yes' : 'no',
                a.utm_source || '', a.utm_medium || '', a.utm_campaign || '', a.utm_content || '', a.referrer || '', a.landing || '',
                a.first_touch ? JSON.stringify(a.first_touch) : '', 'new']);

  if (WHATSAPP_WEBHOOK) {
    try {
      UrlFetchApp.fetch(WHATSAPP_WEBHOOK, { method: 'post', contentType: 'application/json',
        payload: JSON.stringify({ phone: normalizePhone(data.phone), name: data.name, event: data.event, party_size: data.party_size }) });
    } catch (err) {}
  }
  return out({ ok: true });
}

function doGet() { return out({ ok: true, service: 'arshia.wav guest list' }); }

function normalizePhone(p) {
  var d = String(p).replace(/\D/g, '');
  if (d.indexOf('00') === 0) d = d.slice(2);
  if (d.indexOf('05') === 0) d = '971' + d.slice(1);   // local UAE mobile
  if (d.indexOf('5') === 0 && d.length === 9) d = '971' + d;
  return d;
}

function out(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}

/** Run manually from the editor each week: how many sign-ups per source, so you know which videos fill the list. */
function weeklySourceReport() {
  var sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
  var rows = sh.getDataRange().getValues().slice(1);
  var since = new Date(Date.now() - 7 * 86400000);
  var by = {};
  rows.forEach(function (r) {
    if (new Date(r[0]) < since) return;
    var k = (r[7] || 'direct') + ' / ' + (r[10] || '-');
    by[k] = (by[k] || 0) + 1;
  });
  Logger.log(JSON.stringify(by, null, 2));
  return by;
}
