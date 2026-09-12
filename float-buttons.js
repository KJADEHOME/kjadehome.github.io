/* Combined Floating Buttons (WhatsApp + WeChat) — self-contained, ONE file.
   New B2B sites should use this instead of two separate scripts.
   Drop at site root, reference from every page (see inject_component.py).

   === CONFIG ===
   Edit WHATSAPP and WECHAT_ID below for your site.
   - WHATSAPP: bare number with country code, no "+" or spaces (e.g. 8615263130999)
   - WECHAT_ID: your WeChat ID
   - PRESET_MSG: URL-encoded prefilled inquiry text for WhatsApp
*/
(function () {
  if (document.getElementById('b2b-float-root')) return; // idempotent guard

  // ---- EDIT THIS ----
  var WHATSAPP   = '8615263130999';
  var WECHAT_ID  = '15263130999';
  var PRESET_MSG = encodeURIComponent("Hi, I'd like to discuss OEM/ODM cooperation for my brand. Could you share your catalog and a quote?");
  // -------------------

  var css = ''
    + '.b2b-float{position:fixed;right:24px;width:60px;height:60px;border-radius:50%;'
    + 'display:flex;align-items:center;justify-content:center;z-index:9998;cursor:pointer;'
    + 'text-decoration:none;box-shadow:0 4px 12px rgba(0,0,0,.25);transition:transform .3s ease;}'
    + '.b2b-float:hover{transform:scale(1.1);}'
    + '.b2b-float svg{width:32px;height:32px;}'
    + '.b2b-wa{bottom:24px;background:#25D366;}'
    + '.b2b-wc{bottom:96px;background:#07C160;}'
    + '.b2b-wa .tt,.b2b-wc .tt{position:absolute;right:72px;top:50%;transform:translateY(-50%);'
    + 'background:#1a1a2e;color:#fff;padding:8px 16px;border-radius:8px;font-size:14px;font-weight:500;'
    + 'white-space:nowrap;opacity:0;pointer-events:none;transition:opacity .3s ease;}'
    + '.b2b-float:hover .tt{opacity:1;}'
    + '.b2b-wc-popup{position:fixed;bottom:168px;right:24px;width:240px;background:#fff;border-radius:12px;'
    + 'box-shadow:0 8px 30px rgba(0,0,0,.18);z-index:9999;padding:18px;display:none;font-family:inherit;}'
    + '.b2b-wc-popup.open{display:block;}'
    + '.b2b-wc-popup h4{margin:0 0 6px;font-size:15px;color:#07C160;}'
    + '.b2b-wc-popup p{margin:0 0 10px;font-size:13px;color:#444;line-height:1.5;}'
    + '.b2b-wc-popup .id{font-size:18px;font-weight:700;color:#1a1a2e;letter-spacing:1px;}'
    + '.b2b-wc-popup .x{position:absolute;top:8px;right:12px;cursor:pointer;color:#999;font-size:18px;line-height:1;}';

  var style = document.createElement('style');
  style.textContent = css;
  document.head.appendChild(style);

  // WhatsApp button
  var wa = document.createElement('a');
  wa.className = 'b2b-float b2b-wa';
  wa.href = 'https://wa.me/' + WHATSAPP + '?text=' + PRESET_MSG;
  wa.target = '_blank';
  wa.setAttribute('aria-label', 'WhatsApp');
  wa.innerHTML = '<svg viewBox="0 0 24 24" fill="white"><path d="M.057 24l1.687-6.163a11.867 11.867 0 01-1.587-5.946C.16 5.335 5.495 0 12.05 0a11.82 11.82 0 018.413 3.488 11.82 11.82 0 013.48 8.414c-.003 6.557-5.338 11.892-11.893 11.892a11.9 11.9 0 01-5.688-1.448L.057 24zm6.597-3.807c1.676.995 3.276 1.591 5.392 1.592 5.448 0 9.886-4.434 9.889-9.885.002-5.462-4.415-9.89-9.881-9.892-5.452 0-9.887 4.434-9.889 9.884a9.86 9.86 0 001.51 5.26l-.999 3.648 3.978-1.607zm11.387-5.464c-.074-.124-.272-.198-.57-.347-.297-.149-1.758-.868-2.031-.967-.272-.099-.47-.149-.669.149-.198.297-.768.967-.941 1.165-.173.198-.347.223-.644.074-.297-.149-1.255-.462-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.297-.347.446-.521.151-.172.2-.296.3-.495.099-.198.05-.372-.025-.521-.075-.148-.669-1.611-.916-2.206-.242-.579-.487-.501-.669-.51l-.57-.01c-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.095 3.2 5.076 4.487.709.306 1.263.489 1.694.626.712.226 1.36.194 1.872.118.571-.085 1.758-.719 2.006-1.413.248-.695.248-1.29.173-1.414z"/></svg>'
    + '<span class="tt">WhatsApp</span>';

  // WeChat button + popup
  var wc = document.createElement('div');
  wc.className = 'b2b-float b2b-wc';
  wc.setAttribute('role', 'button');
  wc.setAttribute('aria-label', 'WeChat: ' + WECHAT_ID);
  wc.innerHTML = '<svg viewBox="0 0 24 24" fill="white"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/></svg>'
    + '<span class="tt">WeChat: ' + WECHAT_ID + '</span>';

  var popup = document.createElement('div');
  popup.className = 'b2b-wc-popup';
  popup.innerHTML = '<span class="x" aria-label="Close">&times;</span>'
    + '<h4>WeChat</h4><p>Scan or add us on WeChat for fast replies:</p>'
    + '<div class="id">' + WECHAT_ID + '</div>';

  var root = document.createElement('div');
  root.id = 'b2b-float-root';
  root.appendChild(wa); root.appendChild(wc); root.appendChild(popup);
  document.body.appendChild(root);

  function closePopup() { popup.classList.remove('open'); }
  wc.addEventListener('click', function (e) {
    e.stopPropagation();
    if (popup.classList.contains('open')) closePopup(); else popup.classList.add('open');
  });
  popup.querySelector('.x').addEventListener('click', function (e) { e.stopPropagation(); closePopup(); });
  document.addEventListener('click', function (e) {
    if (!popup.contains(e.target) && e.target !== wc) closePopup();
  });
})();
