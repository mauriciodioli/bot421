// dpia-shim.js
(function () {
  if (window.__DPIA_SHIM_ACTIVE__ || window.DPIA_SHIM_DISABLE) return;
  window.__DPIA_SHIM_ACTIVE__ = true;

  // Hook global: endurece <a> y bloquea javascript: en href/src
  if (window.DOMPurify && DOMPurify.addHook) {
    DOMPurify.addHook('afterSanitizeAttributes', (node) => {
      if (node.tagName === 'A') {
        const href = node.getAttribute('href') || '';
        if (/^javascript:/i.test(href)) node.removeAttribute('href');
        node.setAttribute('rel', 'noopener noreferrer');
        node.setAttribute('target', '_blank');
      }
      if (node.tagName === 'IMG') {
        const src = node.getAttribute('src') || '';
        if (/^javascript:/i.test(src)) node.removeAttribute('src');
      }
    });
  }

  function sanitize(str) {
    if (typeof str !== "string" || !window.DOMPurify) return str;
    return window.DOMPurify.sanitize(str);
  }
  function allowRaw(el) {
    try { return !!(el && (el.dataset?.allowRaw === "1" || el.closest?.('[data-allow-raw="1"]'))); }
    catch { return false; }
  }

  // innerHTML
  try {
    const desc = Object.getOwnPropertyDescriptor(Element.prototype, "innerHTML");
    if (desc && desc.set) {
      Object.defineProperty(Element.prototype, "innerHTML", {
        get() { return desc.get.call(this); },
        set(v) { return desc.set.call(this, allowRaw(this) ? v : sanitize(v)); },
        configurable: true,
        enumerable: desc.enumerable
      });
    }
  } catch (e) { console.warn("[DPIA shim] innerHTML", e); }

  // insertAdjacentHTML
  try {
    const orig = Element.prototype.insertAdjacentHTML;
    if (orig) {
      Element.prototype.insertAdjacentHTML = function (pos, html) {
        return orig.call(this, pos, allowRaw(this) ? html : sanitize(html));
      };
    }
  } catch (e) { console.warn("[DPIA shim] insertAdjacentHTML", e); }

  // Range.createContextualFragment
  try {
    const orig = Range.prototype.createContextualFragment;
    if (orig) {
      Range.prototype.createContextualFragment = function (html) {
        return orig.call(this, sanitize(html));
      };
    }
  } catch {}

  // jQuery.html(...)
  if (window.jQuery && jQuery.fn && jQuery.fn.html) {
    const oldHtml = jQuery.fn.html;
    jQuery.fn.html = function (arg) {
      if (arguments.length && typeof arg === "string") {
        const el0 = this.length ? this[0] : null;
        arg = allowRaw(el0) ? arg : sanitize(arg);
        return oldHtml.call(this, arg);
      }
      return oldHtml.call(this);
    };
  }

  // document.cookie endurecido
  try {
    const d = Object.getOwnPropertyDescriptor(Document.prototype, "cookie");
    if (d && d.set) {
      Object.defineProperty(Document.prototype, "cookie", {
        get() { return d.get.call(this); },
        set(val) {
          let v = String(val || "");
          if (!/;\s*Path=/i.test(v)) v += "; Path=/";
          if (location.protocol === "https:" && !/;\s*Secure/i.test(v)) v += "; Secure";
          if (!/;\s*SameSite=/i.test(v)) v += "; SameSite=Lax";
          if (/(\.|^)dpia\.site$/i.test(location.hostname) && !/;\s*Domain=/i.test(v)) v += "; Domain=.dpia.site";
          return d.set.call(this, v);
        },
        configurable: true,
        enumerable: d.enumerable
      });
    }
  } catch (e) { console.warn("[DPIA shim] cookie", e); }

  // Auditoría LS
  try {
    const origSet = Storage.prototype.setItem;
    Storage.prototype.setItem = function (k, v) {
      if (/(token|jwt|bearer|auth)/i.test(String(k))) {
        console.warn("[DPIA audit] Escritura potencialmente sensible en localStorage:", k);
      }
      return origSet.apply(this, arguments);
    };
  } catch {}

  console.info("[DPIA shim] ON (HTML sanitizado, cookies endurecidas, auditoría LS)");
})();
