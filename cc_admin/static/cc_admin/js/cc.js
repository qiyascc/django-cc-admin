(function () {
  "use strict";

  var root = document.documentElement;
  var config = {};
  try { config = JSON.parse(document.getElementById("cc-config").textContent); } catch (e) { config = {}; }
  var isMac = /Mac|iPhone|iPad/.test(navigator.platform || navigator.userAgent);
  var MOD = isMac ? "⌘" : "Ctrl";
  var store = {
    get: function (key, fallback) {
      try { var v = localStorage.getItem("cc-admin:" + key); return v === null ? fallback : JSON.parse(v); } catch (e) { return fallback; }
    },
    set: function (key, value) {
      try { localStorage.setItem("cc-admin:" + key, JSON.stringify(value)); } catch (e) {}
    }
  };

  function $(sel, ctx) { return (ctx || document).querySelector(sel); }
  function $$(sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); }
  function on(el, type, fn, opts) { if (el) el.addEventListener(type, fn, opts); }
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  function icon(name) { return '<svg class="cc-icon" aria-hidden="true"><use href="#cc-i-' + esc(name) + '"></use></svg>'; }
  function typing(e) {
    var t = e.target;
    return t && (t.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName));
  }
  function anyDialogOpen() { return !!$("dialog[open]"); }

  $$("[data-mod]").forEach(function (el) { el.textContent = el.textContent.replace("⌘", MOD + (isMac ? "" : "+")); });

  function readPrefs() {
    var m = document.cookie.match(/(?:^|;\s*)cc_admin_prefs=([^;]*)/);
    if (!m) return {};
    try { return JSON.parse(decodeURIComponent(m[1])) || {}; } catch (e) { return {}; }
  }
  function writePrefs(prefs) {
    document.cookie = "cc_admin_prefs=" + encodeURIComponent(JSON.stringify(prefs)) + ";path=/;max-age=31536000;SameSite=Lax";
  }
  function applyPrefs(prefs) {
    var themes = config.themes || {};
    var theme = themes[prefs.theme] ? prefs.theme : config.theme;
    var meta = themes[theme] || { schemes: ["light", "dark"], layout: "sidebar", css: theme };
    var scheme = prefs.scheme || config.scheme || "auto";
    if (meta.schemes.indexOf(scheme) < 0) scheme = meta.schemes.length === 1 ? meta.schemes[0] : "auto";
    root.dataset.theme = meta.css || theme;
    root.dataset.skin = theme;
    root.dataset.scheme = scheme;
    root.dataset.density = prefs.density || config.density || "comfortable";
    if (!config.forcedLayout) root.dataset.layout = meta.layout;
    syncPanel();
  }
  var prefs = readPrefs();

  function syncPanel() {
    $$("[data-pref]").forEach(function (group) {
      var key = group.dataset.pref;
      var current = key === "theme" ? root.dataset.skin : (prefs[key] || (key === "scheme" ? root.dataset.scheme : root.dataset[key]));
      if (key === "scheme" && !prefs.scheme) current = root.dataset.scheme;
      if (LOOK.indexOf(key) >= 0) current = prefs[key] || "";
      $$("[data-value]", group).forEach(function (btn) { btn.classList.toggle("is-on", btn.dataset.value === current); });
      if (key === "scheme") {
        var meta = (config.themes || {})[root.dataset.skin];
        $$("[data-value]", group).forEach(function (btn) {
          var ok = !meta || meta.schemes.length > 1 || btn.dataset.value === meta.schemes[0];
          btn.disabled = !ok;
          btn.style.opacity = ok ? "" : ".35";
        });
      }
    });
  }

  var LOOK = ["accent", "font", "size", "radius"];
  var RADII = { sharp: "0px", soft: "6px", round: "16px" };
  function contrast(hex) {
    var h = hex.replace("#", "");
    if (h.length === 3) h = h.split("").map(function (c) { return c + c; }).join("");
    var r = parseInt(h.slice(0, 2), 16) / 255, g = parseInt(h.slice(2, 4), 16) / 255, b = parseInt(h.slice(4, 6), 16) / 255;
    return 0.2126 * Math.pow(r, 1.8) + 0.7152 * Math.pow(g, 1.8) + 0.0722 * Math.pow(b, 1.8) > 0.42 ? "#111111" : "#ffffff";
  }
  function applyLook() {
    var st = root.style;
    ["accent", "accent-2", "accent-text", "accent-fg", "chart-1", "heat", "font", "font-head", "size", "radius", "radius-sm", "radius-lg", "btn-radius"].forEach(function (n) { st.removeProperty("--cc-" + n); });
    var tag = $("#cc-user-tokens");
    if (tag) tag.textContent = "";
    var a = prefs.accent;
    if (a && /^#([0-9a-f]{3}|[0-9a-f]{6})$/i.test(a)) {
      st.setProperty("--cc-accent", a);
      st.setProperty("--cc-accent-2", "color-mix(in srgb, " + a + " 84%, black)");
      st.setProperty("--cc-accent-text", a);
      st.setProperty("--cc-accent-fg", contrast(a));
      st.setProperty("--cc-chart-1", a);
      st.setProperty("--cc-heat", a);
    }
    var fonts = config.fonts || {};
    if (prefs.font && fonts[prefs.font]) { st.setProperty("--cc-font", fonts[prefs.font]); st.setProperty("--cc-font-head", fonts[prefs.font]); }
    if (prefs.size && /^\d{2}$/.test(prefs.size)) st.setProperty("--cc-size", prefs.size + "px");
    var r = RADII[prefs.radius];
    if (r) {
      st.setProperty("--cc-radius", r);
      st.setProperty("--cc-radius-sm", "calc(" + r + " * .7)");
      st.setProperty("--cc-radius-lg", "calc(" + r + " * 1.4)");
      st.setProperty("--cc-btn-radius", "calc(" + r + " * .7)");
    }
    var sel = $("[data-pref-select=font]");
    if (sel) sel.value = prefs.font || "";
    var pick = $("[data-accent-pick]");
    if (pick && a) pick.value = a.length === 4 ? "#" + a.slice(1).split("").map(function (c) { return c + c; }).join("") : a;
  }
  function setPref(key, value) {
    if (value) prefs[key] = value; else delete prefs[key];
    writePrefs(prefs);
    applyPrefs(prefs);
    if (LOOK.indexOf(key) >= 0) applyLook();
  }
  on(document, "change", function (e) {
    var sel = e.target.closest("[data-pref-select]");
    if (sel) setPref(sel.dataset.prefSelect, sel.value);
    if (e.target.matches("[data-accent-pick]")) setPref("accent", e.target.value);
  });
  on(document, "input", function (e) {
    if (e.target.matches("[data-accent-pick]")) { prefs.accent = e.target.value; applyLook(); }
  });
  on(document, "click", function (e) {
    if (e.target.closest("[data-appearance-reset]")) { LOOK.forEach(function (k) { delete prefs[k]; }); writePrefs(prefs); applyPrefs(prefs); applyLook(); }
  });
  on(document, "click", function (e) {
    var btn = e.target.closest("[data-pref] [data-value]");
    if (!btn) return;
    var key = btn.closest("[data-pref]").dataset.pref;
    if (LOOK.indexOf(key) >= 0) { setPref(key, btn.dataset.value); return; }
    prefs[key] = btn.dataset.value;
    writePrefs(prefs);
    applyPrefs(prefs);
    $$("[data-theme-open] span").forEach(function (s) {
      var meta = (config.themes || {})[root.dataset.skin];
      if (meta && s.closest(".cc-side-btn")) s.textContent = meta.label;
    });
    $$(".cc-menu-item[data-theme-open] em").forEach(function (s) {
      var meta = (config.themes || {})[root.dataset.skin];
      if (meta) s.textContent = meta.label;
    });
  });

  function openDialog(dlg) {
    if (!dlg) return;
    $$("dialog[open]").forEach(function (d) { if (d !== dlg) d.close(); });
    closeMenus();
    if (!dlg.open) dlg.showModal();
  }
  $$("dialog.cc-dialog, dialog.cc-drawer").forEach(function (dlg) {
    on(dlg, "click", function (e) {
      if (e.target === dlg) {
        var r = dlg.getBoundingClientRect();
        if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) dlg.close();
      }
      if (e.target.closest("[data-close]")) dlg.close();
    });
  });
  on(document, "click", function (e) {
    if (e.target.closest("[data-theme-open]")) { e.preventDefault(); syncPanel(); openDialog($("[data-theme-panel]")); }
    if (e.target.closest("[data-keys-open]")) { e.preventDefault(); openKeys(); }
    var drawer = e.target.closest("[data-drawer-open]");
    if (drawer) { e.preventDefault(); openDialog($('[data-drawer="' + drawer.dataset.drawerOpen + '"]')); }
    if (e.target.closest("[data-palette-open]")) { e.preventDefault(); palette.open(); }
  });

  function closeMenus(except) {
    $$("[data-menu].is-open").forEach(function (m) {
      if (m !== except) {
        m.classList.remove("is-open");
        var t = $("[data-menu-toggle]", m);
        if (t) t.setAttribute("aria-expanded", "false");
      }
    });
  }
  on(document, "click", function (e) {
    var toggle = e.target.closest("[data-menu-toggle]");
    if (toggle) {
      e.preventDefault();
      var menu = toggle.closest("[data-menu]");
      var open = !menu.classList.contains("is-open");
      closeMenus(menu);
      menu.classList.toggle("is-open", open);
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      if (open) {
        var panel = $(".cc-menu", menu);
        menu.classList.remove("is-up");
        if (panel) {
          var rect = panel.getBoundingClientRect();
          if (rect.bottom > window.innerHeight - 8 && rect.top - rect.height > 60) menu.classList.add("is-up");
        }
      }
      return;
    }
    if (!e.target.closest(".cc-menu")) closeMenus();
  });

  var side = $("[data-side]");
  function setSide(open) { root.classList.toggle("cc-side-open", open); }
  on(document, "click", function (e) {
    if (e.target.closest("[data-side-toggle]")) setSide(!root.classList.contains("cc-side-open"));
    if (e.target.closest("[data-side-close]")) setSide(false);
    if (e.target.closest("[data-side-collapse]")) toggleCollapse();
  });
  function toggleCollapse() {
    if (window.matchMedia("(max-width: 960px)").matches) { setSide(!root.classList.contains("cc-side-open")); return; }
    var next = root.dataset.side === "collapsed" ? "" : "collapsed";
    if (next) root.dataset.side = next; else delete root.dataset.side;
    try { if (next) localStorage.setItem("cc-admin:side", next); else localStorage.removeItem("cc-admin:side"); } catch (e) {}
  }

  var collapsedGroups = store.get("groups", {});
  $$(".cc-nav-group[data-group]").forEach(function (g) {
    if (collapsedGroups[g.dataset.group] && !g.classList.contains("is-active")) g.classList.add("is-collapsed");
  });
  on(document, "click", function (e) {
    var t = e.target.closest("[data-group-toggle]");
    if (!t || t.hasAttribute("data-static")) return;
    if (root.dataset.layout === "topbar" && !window.matchMedia("(max-width: 960px)").matches) return;
    var g = t.closest(".cc-nav-group");
    g.classList.toggle("is-collapsed");
    t.setAttribute("aria-expanded", g.classList.contains("is-collapsed") ? "false" : "true");
    if (g.dataset.group) {
      collapsedGroups[g.dataset.group] = g.classList.contains("is-collapsed");
      store.set("groups", collapsedGroups);
    }
  });

  var navFilter = $("[data-nav-filter]");
  on(navFilter, "input", function () {
    var q = navFilter.value.trim().toLowerCase();
    $$(".cc-nav-group").forEach(function (g) {
      var any = false;
      $$("li", g).forEach(function (li) {
        var a = $("[data-nav-item]", li);
        if (!a) return;
        var span = $("span", a);
        var text = span.dataset.text || span.textContent;
        span.dataset.text = text;
        var i = text.toLowerCase().indexOf(q);
        var hit = !q || i >= 0;
        li.hidden = !hit;
        span.innerHTML = q && i >= 0 ? esc(text.slice(0, i)) + "<mark>" + esc(text.slice(i, i + q.length)) + "</mark>" + esc(text.slice(i + q.length)) : esc(text);
        if (hit) any = true;
      });
      g.hidden = !any && !!q;
      if (q) g.classList.remove("is-collapsed");
    });
  });
  on(navFilter, "keydown", function (e) {
    if (e.key === "Enter") {
      var first = $$("[data-nav-item]", side).filter(function (a) { return !a.closest("[hidden]"); })[0];
      if (first) first.click();
    }
    if (e.key === "Escape") { navFilter.value = ""; navFilter.dispatchEvent(new Event("input")); navFilter.blur(); }
  });

  var pinned = store.get("pinned", []);
  function renderPinned() {
    var box = $("[data-pinned]");
    var list = $("[data-pinned-list]");
    if (!box || !list) return;
    list.innerHTML = "";
    pinned.forEach(function (key) {
      var source = $('.cc-nav-group:not(.cc-nav-pinned) [data-key="' + key + '"]');
      if (!source) return;
      var li = source.closest("li").cloneNode(true);
      list.appendChild(li);
    });
    box.hidden = !list.children.length;
    $$("[data-pin]").forEach(function (b) { b.classList.toggle("is-on", pinned.indexOf(b.dataset.pin) >= 0); });
  }
  renderPinned();
  on(document, "click", function (e) {
    var b = e.target.closest("[data-pin]");
    if (!b) return;
    var key = b.dataset.pin;
    var i = pinned.indexOf(key);
    if (i >= 0) pinned.splice(i, 1); else pinned.push(key);
    store.set("pinned", pinned);
    renderPinned();
    toast(i >= 0 ? "Removed from pinned" : "Pinned to the menu");
  });

  function toast(text, tone) {
    var box = $("[data-toasts]");
    if (!box) {
      box = document.createElement("ul");
      box.className = "cc-toasts";
      box.setAttribute("data-toasts", "");
      document.body.appendChild(box);
    }
    var li = document.createElement("li");
    li.className = "cc-toast " + (tone || "success");
    li.innerHTML = icon(tone === "error" ? "circle-exclamation-point" : "circle-check") + "<span>" + esc(text) + "</span>";
    box.appendChild(li);
    setTimeout(function () { dismiss(li); }, 2600);
  }
  function dismiss(li) {
    if (!li || li.classList.contains("is-leaving")) return;
    li.classList.add("is-leaving");
    setTimeout(function () { li.remove(); }, 260);
  }
  $$("[data-toasts] .cc-toast").forEach(function (li, i) {
    if (!li.classList.contains("error") && !li.classList.contains("warning")) setTimeout(function () { dismiss(li); }, 6000 + i * 400);
  });
  on(document, "click", function (e) {
    var b = e.target.closest("[data-dismiss]");
    if (b) dismiss(b.closest(".cc-toast"));
  });

  on(document, "click", function (e) {
    var b = e.target.closest("[data-copy]");
    if (!b) return;
    e.preventDefault();
    e.stopPropagation();
    var done = function () { b.classList.add("is-done"); setTimeout(function () { b.classList.remove("is-done"); }, 1200); };
    if (navigator.clipboard) navigator.clipboard.writeText(b.dataset.copy).then(done, function () {});
  });

  function paintAvatars(ctx) {
    $$(".cc-avatar[data-seed]", ctx).forEach(function (a) {
      var s = a.dataset.seed || "", h = 0;
      for (var i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) % 360;
      a.style.setProperty("--h", h);
    });
  }
  paintAvatars();

  $$("[data-heat]").forEach(function (h) { h.scrollLeft = h.scrollWidth; });
  var heatTip = null;
  on(document, "mouseover", function (e) {
    var cell = e.target.closest("[data-heat] a[data-day]");
    if (!cell) { if (heatTip) heatTip.hidden = true; return; }
    if (!heatTip) { heatTip = document.createElement("div"); heatTip.className = "cc-heat-tip"; document.body.appendChild(heatTip); }
    heatTip.textContent = cell.getAttribute("aria-label");
    heatTip.hidden = false;
    var r = cell.getBoundingClientRect();
    heatTip.style.left = (r.left + r.width / 2 + window.scrollX) + "px";
    heatTip.style.top = (r.top + window.scrollY - 8) + "px";
  });
  function loadFeed(href, push) {
    var feed = $("[data-activity-feed]");
    if (!feed) { location.href = href; return; }
    feed.classList.add("is-loading");
    var day = (href.match(/[?&]day=([\d-]+)/) || [])[1] || "";
    $$("[data-heat] a[data-day]").forEach(function (c) { c.classList.toggle("is-selected", c.dataset.day === day); });
    fetch(href + (href.indexOf("?") >= 0 ? "&" : "?") + "partial=1", { credentials: "same-origin", headers: { "X-Requested-With": "XMLHttpRequest" } })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.text(); })
      .then(function (html) {
        var tmp = document.createElement("div");
        tmp.innerHTML = html;
        var fresh = $("[data-activity-feed]", tmp);
        if (!fresh) throw new Error("empty");
        feed.replaceWith(fresh);
        paintAvatars(fresh);
        if (push) history.pushState({ feed: href }, "", href);
        if (day && fresh.getBoundingClientRect().top > window.innerHeight * 0.8) fresh.scrollIntoView({ behavior: "smooth", block: "start" });
      })
      .catch(function () { location.href = href; });
  }
  on(document, "click", function (e) {
    var a = e.target.closest("[data-heat] a[data-day], [data-day-clear]");
    if (!a || e.metaKey || e.ctrlKey || e.shiftKey || !$("[data-activity-feed]")) return;
    e.preventDefault();
    var href = a.getAttribute("href");
    if (a.classList.contains("is-selected")) href = href.replace(/([?&])day=[^&]*&?/, "$1").replace(/[?&]$/, "") || "?";
    loadFeed(href, true);
  });
  on(document, "click", function (e) {
    var b = e.target.closest("[data-feed-more-btn]");
    if (!b) return;
    $$("[data-feed-more]", b.parentNode).forEach(function (m) { m.hidden = false; });
    b.remove();
  });
  on(window, "popstate", function () { if ($("[data-activity-feed]")) loadFeed(location.search || "?", false); });

  var greet = $("[data-greeting-text]");
  if (greet) {
    var hour = new Date().getHours();
    greet.textContent = hour < 5 ? "Working late" : hour < 12 ? "Good morning" : hour < 18 ? "Good afternoon" : "Good evening";
  }

  var confirmDlg = $("[data-confirm-dialog]");
  on(document, "click", function (e) {
    var b = e.target.closest("[data-confirm]");
    if (!b || !confirmDlg || b.dataset.confirmed) return;
    e.preventDefault();
    $("[data-confirm-text]", confirmDlg).textContent = b.dataset.confirm;
    confirmDlg.returnValue = "";
    openDialog(confirmDlg);
    confirmDlg.onclose = function () {
      if (confirmDlg.returnValue !== "yes") return;
      b.dataset.confirmed = "1";
      if (b.form && b.type === "submit") {
        if (b.form.requestSubmit) b.form.requestSubmit(b); else b.click();
      } else b.click();
      delete b.dataset.confirmed;
    };
  }, true);

  var recent = store.get("recent", []);
  var titleEl = $("[data-recent-title]");
  if (titleEl) {
    var entry = { title: titleEl.textContent.trim(), model: titleEl.dataset.recentModel || "", url: location.pathname, at: Date.now() };
    recent = [entry].concat(recent.filter(function (r) { return r.url !== entry.url; })).slice(0, 12);
    store.set("recent", recent);
  }
  function renderRecent(ctx) { $$("[data-recent-list]", ctx).forEach(function (list) {
    if (!recent.length) { list.innerHTML = '<li class="cc-muted cc-list-empty">' + esc(list.dataset.empty) + "</li>"; return; }
    list.innerHTML = recent.slice(0, 7).map(function (r) {
      return '<li><a class="cc-list-row" href="' + esc(r.url) + '"><span class="cc-list-icon">' + icon("rotate-ccw-clock") + '</span><span class="cc-list-text"><b>' + esc(r.title) + "</b><small>" + esc(r.model) + '</small></span><span class="cc-list-meta">' + ago(r.at) + "</span></a></li>";
    }).join("");
  }); }
  renderRecent();
  function ago(t) {
    var s = Math.max(1, Math.round((Date.now() - t) / 1000));
    if (s < 60) return "just now";
    var m = Math.round(s / 60); if (m < 60) return m + "m ago";
    var h = Math.round(m / 60); if (h < 24) return h + "h ago";
    var d = Math.round(h / 24); return d + "d ago";
  }

  var palette = (function () {
    var dlg = $("[data-palette]");
    var input = dlg && $("[data-palette-input]", dlg);
    var list = dlg && $("[data-palette-list]", dlg);
    var hint = dlg && $("[data-palette-hint]", dlg);
    var items = [], active = 0, timer = null, remote = [], lastQuery = "", seq = 0;

    function base() {
      var out = [];
      var nav = $$("[data-nav-item]", side || document).map(function (a) {
        var group = a.closest(".cc-nav-group");
        var title = $(".cc-nav-title span", group || document);
        var span = $("span", a);
        var use = $("use", a);
        return {
          title: span ? (span.dataset.text || span.textContent).trim() : a.textContent.trim(),
          sub: title && group && !group.classList.contains("cc-nav-pinned") ? title.textContent.trim() : "",
          url: a.getAttribute("href"),
          icon: use ? use.getAttribute("href").replace("#cc-i-", "") : "arrow-right",
          kind: "Go to",
          group: "Navigate"
        };
      });
      var seen = {};
      nav.forEach(function (n) { if (n.url && !seen[n.url]) { seen[n.url] = 1; out.push(n); } });
      (config.models || []).forEach(function (m) {
        if (m.add) out.push({ title: "New " + m.title.replace(/s$/, "").toLowerCase(), sub: m.app, url: m.add, icon: "plus", kind: "Create", group: "Actions" });
      });
      recent.slice(0, 6).forEach(function (r) { out.push({ title: r.title, sub: r.model, url: r.url, icon: "rotate-ccw-clock", kind: "Recent", group: "Recent" }); });
      if (config.switcher) {
        Object.keys(config.themes || {}).forEach(function (key) {
          out.push({ title: "Theme: " + config.themes[key].label, sub: config.themes[key].layout + " layout", icon: "palette", kind: "Theme", group: "Appearance", run: function () { prefs.theme = key; writePrefs(prefs); applyPrefs(prefs); } });
        });
        ["light", "dark", "auto"].forEach(function (s) {
          out.push({ title: "Switch to " + s + " mode", icon: s === "light" ? "sun" : s === "dark" ? "moon" : "monitor", kind: "Mode", group: "Appearance", run: function () { prefs.scheme = s; writePrefs(prefs); applyPrefs(prefs); } });
        });
      }
      (config.commands || []).forEach(function (c) { out.push({ title: c.title, sub: c.sub || c.keywords, url: c.url, icon: c.icon, kind: "Open", group: c.group || "Commands" }); });
      if (config.activity) out.push({ title: "My activity", sub: "Changes and contribution calendar", url: config.activity, icon: "activity", kind: "Go to", group: "Navigate" });
      if (sc.enabled) out.push({ title: "Keyboard shortcuts", icon: "keyboard", kind: "Help", group: "Help", run: function () { openKeys(); } });
      return out;
    }

    function score(text, q) {
      text = text.toLowerCase();
      var i = text.indexOf(q);
      if (i === 0) return 100 - text.length / 100;
      if (i > 0) return (text.charAt(i - 1) === " " ? 80 : 60) - i / 100;
      var ti = 0, gaps = 0;
      for (var qi = 0; qi < q.length; qi++) {
        var f = text.indexOf(q.charAt(qi), ti);
        if (f < 0) return 0;
        gaps += f - ti;
        ti = f + 1;
      }
      return Math.max(1, 40 - gaps);
    }
    function highlight(text, q) {
      if (!q) return esc(text);
      var i = text.toLowerCase().indexOf(q);
      if (i < 0) return esc(text);
      return esc(text.slice(0, i)) + "<mark>" + esc(text.slice(i, i + q.length)) + "</mark>" + esc(text.slice(i + q.length));
    }

    function render() {
      var q = input.value.trim().toLowerCase();
      var all = base();
      if (q) {
        all = all.map(function (it) { it._s = Math.max(score(it.title, q), it.sub ? score(it.sub, q) * 0.6 : 0); return it; })
          .filter(function (it) { return it._s > 0; })
          .sort(function (a, b) { return b._s - a._s; })
          .slice(0, 30);
        all = all.concat(remote.map(function (r) { return { title: r.title, sub: r.model, url: r.url, icon: r.icon || "file-text", kind: "Record", group: "Records" }; }));
      } else {
        all = all.filter(function (it) { return it.group === "Recent" || it.group === "Navigate"; }).slice(0, 14);
      }
      items = all;
      active = Math.min(active, Math.max(0, items.length - 1));
      var html = "", group = null;
      if (!items.length) html = '<div class="cc-palette-empty">' + (q.length >= (config.minLength || 2) && config.searchModels ? "No matches. Still looking in records…" : "No matches") + "</div>";
      var order = ["Recent", "Navigate", "Records", "Actions", "Appearance", "Help"];
      var rank = function (g) { var i = order.indexOf(g); return i < 0 ? 2.5 : i; };
      if (q) {
        items.sort(function (a, b) { return rank(a.group) - rank(b.group) || (b._s || 0) - (a._s || 0); });
      }
      items.forEach(function (it, i) {
        if (it.group !== group) { group = it.group; html += '<div class="cc-palette-group">' + esc(group) + "</div>"; }
        html += '<a class="cc-palette-item' + (i === active ? " is-active" : "") + '" data-i="' + i + '"' + (it.url ? ' href="' + esc(it.url) + '"' : ' href="#"') + ' role="option">' +
          '<span class="cc-pi-icon">' + icon(it.icon || "arrow-right") + '</span><span class="cc-pi-text"><b>' + highlight(it.title, q) + "</b>" + (it.sub ? "<small>" + esc(it.sub) + "</small>" : "") + '</span><span class="cc-pi-kind">' + esc(it.kind || "") + "</span>" + icon("corner-down-left").replace("cc-icon", "cc-icon cc-pi-enter") + "</a>";
      });
      list.innerHTML = html;
      scrollActive();
    }
    function scrollActive() {
      var el = $(".cc-palette-item.is-active", list);
      if (el) el.scrollIntoView({ block: "nearest" });
    }
    function move(d) {
      if (!items.length) return;
      active = (active + d + items.length) % items.length;
      $$(".cc-palette-item", list).forEach(function (el) { el.classList.toggle("is-active", +el.dataset.i === active); });
      scrollActive();
    }
    function choose(i, newTab) {
      var it = items[i];
      if (!it) return;
      if (it.run) { dlg.close(); it.run(); return; }
      if (newTab) window.open(it.url, "_blank"); else location.href = it.url;
    }
    function search(q) {
      clearTimeout(timer);
      if (!config.searchModels || !config.search || q.length < (config.minLength || 2)) { remote = []; hint.innerHTML = ""; return; }
      if (q === lastQuery) return;
      timer = setTimeout(function () {
        var mine = ++seq;
        lastQuery = q;
        hint.innerHTML = '<span class="cc-palette-spin"></span>';
        fetch(config.search + "?q=" + encodeURIComponent(q), { credentials: "same-origin", headers: { "X-Requested-With": "XMLHttpRequest" } })
          .then(function (r) { return r.ok ? r.json() : { results: [] }; })
          .then(function (data) {
            if (mine !== seq) return;
            remote = data.results || [];
            hint.textContent = remote.length ? remote.length + " record" + (remote.length === 1 ? "" : "s") : "";
            render();
          })
          .catch(function () { hint.textContent = ""; });
      }, 180);
    }
    if (dlg) {
      on(input, "input", function () { active = 0; remote = []; lastQuery = ""; render(); search(input.value.trim()); });
      on(input, "keydown", function (e) {
        if (e.key === "ArrowDown" || (e.ctrlKey && e.key === "n")) { e.preventDefault(); move(1); }
        else if (e.key === "ArrowUp" || (e.ctrlKey && e.key === "p")) { e.preventDefault(); move(-1); }
        else if (e.key === "Enter") { e.preventDefault(); choose(active, e.metaKey || e.ctrlKey); }
      });
      on(list, "click", function (e) {
        var a = e.target.closest(".cc-palette-item");
        if (!a) return;
        var it = items[+a.dataset.i];
        if (it && it.run) { e.preventDefault(); choose(+a.dataset.i); }
      });
      on(list, "mousemove", function (e) {
        var a = e.target.closest(".cc-palette-item");
        if (a && +a.dataset.i !== active) { active = +a.dataset.i; $$(".cc-palette-item", list).forEach(function (el) { el.classList.toggle("is-active", el === a); }); }
      });
    }
    return {
      open: function () {
        if (!dlg) return;
        openDialog(dlg);
        input.value = "";
        remote = []; lastQuery = ""; active = 0;
        hint.innerHTML = "";
        render();
        input.focus();
      }
    };
  })();

  var changelist = $("#changelist");
  var results = changelist && $("#result_list");
  var actionbar = $("[data-actionbar]");
  function updateActionbar() {
    if (!actionbar) return;
    var n = $$("input.action-select:checked").length;
    var all = $("#action-toggle");
    actionbar.classList.toggle("is-visible", n > 0 || (all && all.checked));
  }
  if (actionbar) {
    on(document, "change", function (e) { if (e.target.matches(".action-select, #action-toggle")) setTimeout(updateActionbar, 0); });
    on($("[data-actionbar-clear]"), "click", function () {
      $$("input.action-select:checked").forEach(function (cb) { cb.click(); });
      var all = $("#action-toggle");
      if (all && all.checked) all.click();
      var clear = $(".actions .clear a");
      if (clear && clear.offsetParent) clear.click();
      setTimeout(updateActionbar, 0);
    });
    setTimeout(updateActionbar, 50);
  }

  var cursor = -1;
  function rows() { return results ? $$("tbody tr[data-row]", results) : []; }
  function setCursor(i) {
    var r = rows();
    if (!r.length) return;
    cursor = Math.max(0, Math.min(r.length - 1, i));
    r.forEach(function (row, k) { row.classList.toggle("is-cursor", k === cursor); });
    r[cursor].scrollIntoView({ block: "nearest" });
  }
  function openRow(newTab) {
    var row = rows()[cursor];
    if (!row) return;
    var a = $("th a, td a:not(.related-widget-wrapper-link)", row);
    if (!a) return;
    if (newTab) window.open(a.href, "_blank"); else location.href = a.href;
  }

  var applyCols = function () {};
  if (changelist) {
    var key = "cols:" + changelist.dataset.model;
    var hiddenCols = store.get(key, []);
    var menu = $("[data-columns-menu]");
    var holder = $("[data-columns-list]");
    var headers = results ? $$("thead th", results) : [];
    applyCols = function () {
      headers.forEach(function (th, i) {
        var hide = hiddenCols.indexOf(i) >= 0;
        th.classList.toggle("cc-col-hidden", hide);
        rows().forEach(function (tr) { if (tr.children[i]) tr.children[i].classList.toggle("cc-col-hidden", hide); });
      });
    }
    if (menu && headers.length > 2) {
      headers.forEach(function (th, i) {
        if (th.classList.contains("action-checkbox-column") || th.classList.contains("column-cc_row_actions")) return;
        var text = th.textContent.trim();
        if (!text) return;
        var label = document.createElement("label");
        label.className = "cc-menu-item";
        label.innerHTML = '<input type="checkbox"' + (hiddenCols.indexOf(i) < 0 ? " checked" : "") + "><span>" + esc(text) + "</span>";
        on($("input", label), "change", function (e) {
          var pos = hiddenCols.indexOf(i);
          if (e.target.checked && pos >= 0) hiddenCols.splice(pos, 1);
          if (!e.target.checked && pos < 0) hiddenCols.push(i);
          store.set(key, hiddenCols);
          applyCols();
        });
        holder.appendChild(label);
      });
      if (holder.children.length) menu.hidden = false;
      applyCols();
    }
    on(results, "click", function (e) {
      var tr = e.target.closest("tr[data-row]");
      if (tr) { var i = rows().indexOf(tr); if (i >= 0) { cursor = i; rows().forEach(function (r, k) { r.classList.toggle("is-cursor", k === i); }); } }
    });
  }

  $$("[data-filter-select]").forEach(function (sel) {
    on(sel, "change", function () { location.href = sel.value; });
  });
  $$("[data-filter-form]").forEach(function (form) {
    on(form, "submit", function () {
      $$("input, select", form).forEach(function (el) { if (!el.name || el.type === "checkbox" || el.type === "hidden") return; if (el.value === "") el.disabled = true; });
      $$("[data-slider] input[type=range]", form).forEach(function (el, i) { if ((i % 2 === 0 && el.value === el.min) || (i % 2 === 1 && el.value === el.max)) el.disabled = true; });
    });
  });

  var form = $("[data-cc-form]");
  var dirty = false;
  if (form) {
    var tabs = $("[data-tabs]");
    if (tabs) {
      var main = $(".cc-form-main", form);
      main.classList.add("cc-tabbed");
      var tabButtons = $$("[data-tab]", tabs);
      function show(name) {
        tabButtons.forEach(function (b) { b.classList.toggle("is-active", b.dataset.tab === name); b.setAttribute("aria-selected", b.dataset.tab === name ? "true" : "false"); });
        $$("[data-tab-panel]", main).forEach(function (p) { p.classList.toggle("is-active", p.dataset.tabPanel === name); });
        $$("[data-tab-panel-extra]", main).forEach(function (p) { p.classList.toggle("is-active", p.dataset.tabPanelExtra === name); });
        if (history.replaceState) history.replaceState(null, "", "#tab-" + name);
      }
      var firstError = null;
      tabButtons.forEach(function (b) {
        var panel = $('[data-tab-panel="' + b.dataset.tab + '"]', main);
        if (panel && $(".errors, .errorlist", panel)) { b.classList.add("has-error"); if (!firstError) firstError = b.dataset.tab; }
        on(b, "click", function () { show(b.dataset.tab); });
      });
      var fromHash = (location.hash.match(/^#tab-(.+)$/) || [])[1];
      show(firstError || (fromHash && $('[data-tab="' + fromHash + '"]', tabs) ? fromHash : "general"));
    }

    var dirtyFlag = $("[data-dirty]", form);
    if (form.hasAttribute("data-warn-unsaved")) {
      var markDirty = function (e) {
        if (e && e.target && e.target.closest && e.target.closest(".selector-filter, .cc-search-box")) return;
        if (!dirty) { dirty = true; $$("[data-dirty]").forEach(function (d) { d.hidden = false; }); }
      };
      on(form, "input", markDirty);
      on(form, "change", markDirty);
      on(form, "submit", function () { dirty = false; });
      on(window, "beforeunload", function (e) { if (dirty) { e.preventDefault(); e.returnValue = ""; } });
    }

    var cond = form.dataset.conditional;
    if (cond) {
      var rules = {};
      try { rules = JSON.parse(cond); } catch (e) { rules = {}; }
      var values = function () {
        var v = {};
        $$("input, select, textarea", form).forEach(function (el) {
          if (!el.name || el.name.indexOf("-") >= 0) return;
          if (el.type === "checkbox") {
            if ($$('input[type=checkbox][name="' + el.name + '"]', form).length > 1) { v[el.name] = v[el.name] || []; if (el.checked) v[el.name].push(el.value); }
            else v[el.name] = el.checked;
          } else if (el.type === "radio") { if (el.checked) v[el.name] = el.value; else if (!(el.name in v)) v[el.name] = ""; }
          else if (el.multiple) v[el.name] = $$("option:checked", el).map(function (o) { return o.value; });
          else v[el.name] = el.value;
        });
        return v;
      };
      var compiled = {};
      Object.keys(rules).forEach(function (field) { compiled[field] = compile(rules[field]); });
      var evaluate = function () {
        var v = values();
        Object.keys(compiled).forEach(function (field) {
          var show = true;
          try { show = !!compiled[field](v); } catch (e) { show = true; }
          $$('[data-field="' + field + '"]', form).forEach(function (box) {
            box.classList.toggle("cc-cond-hidden", !show);
            var row = box.closest(".cc-row");
            if (row) row.classList.toggle("cc-cond-hidden", !$$(".cc-field", row).some(function (f) { return !f.classList.contains("cc-cond-hidden") && !f.classList.contains("hidden"); }));
          });
        });
      };
      on(form, "input", evaluate);
      on(form, "change", evaluate);
      evaluate();
    }

    $$(".cc-sortable[data-order-field]", form).forEach(sortable);
  }

  function csrf() {
    var input = $("#cc-action-form input[name=csrfmiddlewaretoken]");
    return input ? input.value : "";
  }

  on(document, "click", function (e) {
    var b = e.target.closest("[data-expand]");
    if (!b) return;
    var tr = b.closest("tr");
    var next = tr && tr.nextElementSibling;
    if (!next || !next.hasAttribute("data-section-row")) return;
    var open = next.hidden;
    next.hidden = !open;
    b.setAttribute("aria-expanded", open ? "true" : "false");
    tr.classList.toggle("is-expanded", open);
  });

  var wireSort = function () {};
  if (changelist && changelist.dataset.sortUrl && results) {
    var body = $("tbody", results);
    var dragRow = null;
    wireSort = function () { $$("tr[data-row]", body).forEach(function (tr) {
      var handle = $("[data-row-drag]", tr);
      if (!handle || tr.dataset.ccSort) return;
      tr.dataset.ccSort = "1";
      on(handle, "mousedown", function () { tr.draggable = true; });
      on(handle, "touchstart", function () { tr.draggable = true; }, { passive: true });
      on(tr, "dragstart", function (e) { dragRow = tr; tr.classList.add("is-dragging"); e.dataTransfer.effectAllowed = "move"; try { e.dataTransfer.setData("text/plain", ""); } catch (x) {} });
      on(tr, "dragover", function (e) {
        if (!dragRow || dragRow === tr) return;
        e.preventDefault();
        var r = tr.getBoundingClientRect();
        var after = e.clientY > r.top + r.height / 2;
        var anchor = after ? tr.nextElementSibling : tr;
        if (after && anchor && anchor.hasAttribute("data-section-row")) anchor = anchor.nextElementSibling;
        var detail = dragRow.nextElementSibling && dragRow.nextElementSibling.hasAttribute("data-section-row") ? dragRow.nextElementSibling : null;
        body.insertBefore(dragRow, anchor);
        if (detail) body.insertBefore(detail, dragRow.nextSibling);
      });
      on(tr, "dragend", function () {
        tr.draggable = false;
        tr.classList.remove("is-dragging");
        if (!dragRow) return;
        dragRow = null;
        var data = new FormData();
        $$("tr[data-row]", body).forEach(function (row) { data.append("pk", row.dataset.pk); });
        fetch(changelist.dataset.sortUrl, { method: "POST", body: data, credentials: "same-origin", headers: { "X-CSRFToken": csrf(), "X-Requested-With": "XMLHttpRequest" } })
          .then(function (r) { toast(r.ok ? "Order saved" : "Could not save the order", r.ok ? "success" : "error"); })
          .catch(function () { toast("Could not save the order", "error"); });
      });
    }); };
    wireSort();
  }

  on(document, "change", function (e) {
    var sel = e.target.closest("[data-per-page]");
    if (!sel) return;
    var m = document.cookie.match(/(?:^|;\s*)cc_admin_per=([^;]*)/);
    var per = {};
    try { per = m ? JSON.parse(decodeURIComponent(m[1])) : {}; } catch (x) { per = {}; }
    per[sel.dataset.perPage] = +sel.value;
    document.cookie = "cc_admin_per=" + encodeURIComponent(JSON.stringify(per)) + ";path=/;max-age=31536000;SameSite=Lax";
    var url = new URL(location.href);
    url.searchParams.delete("p");
    location.href = url.toString();
  });

  if (changelist && changelist.hasAttribute("data-top-scroll")) {
    var wrap = $("[data-results]", changelist);
    if (wrap) {
      var top = document.createElement("div");
      top.className = "cc-top-scroll";
      top.innerHTML = "<div></div>";
      wrap.parentNode.insertBefore(top, wrap);
      var sync = function () { top.firstChild.style.width = wrap.scrollWidth + "px"; top.hidden = wrap.scrollWidth <= wrap.clientWidth + 1; };
      var lock = false;
      on(top, "scroll", function () { if (lock) { lock = false; return; } lock = true; wrap.scrollLeft = top.scrollLeft; });
      on(wrap, "scroll", function () { if (lock) { lock = false; return; } lock = true; top.scrollLeft = wrap.scrollLeft; });
      on(window, "resize", sync);
      sync();
    }
  }

  $$("[data-slider]").forEach(function (box) {
    var inputs = $$("input[type=range]", box);
    var lo = inputs[0], hi = inputs[1];
    var outLo = $("[data-slider-lo]", box.parentNode), outHi = $("[data-slider-hi]", box.parentNode);
    var min = parseFloat(lo.min), max = parseFloat(lo.max);
    function paint(e) {
      var a = parseFloat(lo.value), b = parseFloat(hi.value);
      if (a > b) { if (e && e.target === lo) lo.value = b; else hi.value = a; }
      a = parseFloat(lo.value); b = parseFloat(hi.value);
      var span = max - min || 1;
      box.style.setProperty("--lo", ((a - min) / span * 100) + "%");
      box.style.setProperty("--hi", ((b - min) / span * 100) + "%");
      if (outLo) outLo.textContent = (+a).toLocaleString();
      if (outHi) outHi.textContent = (+b).toLocaleString();
    }
    inputs.forEach(function (i) { on(i, "input", paint); });
    paint();
  });

  on(document, "click", function (e) {
    var b = e.target.closest("[data-preset]");
    if (!b) return;
    var box = b.closest(".cc-filter");
    var inputs = $$("input[type=date]", box);
    if (inputs.length < 2) return;
    var d = new Date(), from = new Date(d), to = new Date(d);
    var p = b.dataset.preset;
    if (p === "yesterday") { from.setDate(d.getDate() - 1); to = new Date(from); }
    else if (p === "7" || p === "30") from.setDate(d.getDate() - (+p - 1));
    else if (p === "month") from = new Date(d.getFullYear(), d.getMonth(), 1);
    else if (p === "year") from = new Date(d.getFullYear(), 0, 1);
    var iso = function (x) { return x.getFullYear() + "-" + String(x.getMonth() + 1).padStart(2, "0") + "-" + String(x.getDate()).padStart(2, "0"); };
    inputs[0].value = iso(from);
    inputs[1].value = iso(to);
    $$("[data-preset]", box).forEach(function (x) { x.classList.toggle("is-on", x === b); });
  });

  $$("input[data-cc-color]").forEach(function (input) {
    var wrap = document.createElement("span");
    wrap.className = "cc-color";
    input.parentNode.insertBefore(wrap, input);
    var pick = document.createElement("input");
    pick.type = "color";
    pick.tabIndex = -1;
    wrap.appendChild(pick);
    wrap.appendChild(input);
    var sync = function () { if (/^#[0-9a-f]{6}$/i.test(input.value)) pick.value = input.value; wrap.style.setProperty("--c", input.value || "transparent"); };
    on(pick, "input", function () { input.value = pick.value; sync(); input.dispatchEvent(new Event("change", { bubbles: true })); });
    on(input, "input", sync);
    sync();
  });

  function cleanHtml(html) {
    var doc = new DOMParser().parseFromString("<div>" + html + "</div>", "text/html");
    var allowed = /^(P|BR|B|STRONG|I|EM|U|S|A|UL|OL|LI|H2|H3|H4|BLOCKQUOTE|CODE|PRE|HR|SPAN|DIV)$/;
    (function walk(node) {
      Array.prototype.slice.call(node.children).forEach(function (el) {
        if (!allowed.test(el.tagName)) { if (/^(SCRIPT|STYLE|IFRAME|OBJECT|EMBED)$/.test(el.tagName)) el.remove(); else { walk(el); el.replaceWith.apply(el, Array.prototype.slice.call(el.childNodes)); } return; }
        Array.prototype.slice.call(el.attributes).forEach(function (a) {
          if (el.tagName === "A" && a.name === "href" && !/^\s*(javascript|data|vbscript):/i.test(a.value)) return;
          el.removeAttribute(a.name);
        });
        walk(el);
      });
    })(doc.body.firstChild);
    return doc.body.firstChild.innerHTML;
  }
  var RICH = {
    bold: ["type", "bold"], italic: ["italic", "italic"], underline: ["underline", "underline"], strike: ["strikethrough", "strikethrough"],
    h2: ["heading-2", "formatBlock", "h2"], h3: ["heading-3", "formatBlock", "h3"], quote: ["text-quote", "formatBlock", "blockquote"],
    ul: ["list", "insertUnorderedList"], ol: ["list-ordered", "insertOrderedList"], code: ["code", "formatBlock", "pre"],
    link: ["link", "createLink"], clear: ["remove-formatting", "removeFormat"]
  };
  $$("textarea[data-cc-rich]").forEach(function (ta) {
    var box = document.createElement("div");
    box.className = "cc-rich";
    var bar = document.createElement("div");
    bar.className = "cc-rich-bar";
    ta.dataset.ccRich.split(",").forEach(function (name) {
      var t = RICH[name.trim()];
      if (!t) return;
      var b = document.createElement("button");
      b.type = "button";
      b.title = name;
      b.setAttribute("form", "cc-detached");
      b.innerHTML = icon(t[0]);
      on(b, "mousedown", function (e) { e.preventDefault(); });
      on(b, "click", function () {
        ed.focus();
        if (t[1] === "createLink") { var u = prompt("Link address"); if (u && !/^\s*(javascript|data|vbscript):/i.test(u)) document.execCommand("createLink", false, u); }
        else if (t[1] === "formatBlock") document.execCommand("formatBlock", false, document.queryCommandValue("formatBlock").toLowerCase() === t[2] ? "p" : t[2]);
        else document.execCommand(t[1], false, null);
        sync();
      });
      bar.appendChild(b);
    });
    var ed = document.createElement("div");
    ed.className = "cc-rich-body";
    ed.contentEditable = "true";
    ed.innerHTML = cleanHtml(ta.value);
    var sync = function () { ta.value = ed.innerHTML === "<br>" ? "" : ed.innerHTML; ta.dispatchEvent(new Event("input", { bubbles: true })); };
    on(ed, "input", sync);
    on(ed, "paste", function (e) {
      var html = e.clipboardData && e.clipboardData.getData("text/html");
      if (!html) return;
      e.preventDefault();
      document.execCommand("insertHTML", false, cleanHtml(html));
    });
    ta.parentNode.insertBefore(box, ta);
    box.appendChild(bar);
    box.appendChild(ed);
    box.appendChild(ta);
    ta.hidden = true;
  });

  $$("textarea[data-cc-code]").forEach(function (ta) {
    var grow = function () { ta.style.height = "auto"; ta.style.height = Math.min(640, ta.scrollHeight + 4) + "px"; };
    on(ta, "keydown", function (e) {
      if (e.key !== "Tab" || e.metaKey || e.ctrlKey) return;
      e.preventDefault();
      var s0 = ta.selectionStart, s1 = ta.selectionEnd;
      ta.setRangeText("  ", s0, s1, "end");
    });
    on(ta, "input", grow);
    grow();
    if (ta.dataset.ccCode === "json") {
      var note = document.createElement("div");
      note.className = "cc-code-note";
      ta.parentNode.insertBefore(note, ta.nextSibling);
      var check = function () {
        var v = ta.value.trim();
        if (!v) { note.textContent = ""; ta.classList.remove("is-invalid"); return; }
        try { JSON.parse(v); note.textContent = "Valid JSON"; note.className = "cc-code-note is-ok"; ta.classList.remove("is-invalid"); }
        catch (x) { note.textContent = x.message; note.className = "cc-code-note is-bad"; ta.classList.add("is-invalid"); }
      };
      on(ta, "input", check);
      check();
    }
  });

  $$("input[type=file][data-cc-preview]").forEach(function (input) {
    var box = input.closest(".cc-field") || input.parentNode;
    var img = document.createElement("img");
    img.className = "cc-preview";
    var current = $("a[href]", input.parentNode);
    if (current && /\.(png|jpe?g|gif|webp|svg|avif)(\?|$)/i.test(current.getAttribute("href"))) img.src = current.href;
    else img.hidden = true;
    input.parentNode.insertBefore(img, input.parentNode.firstChild);
    on(input, "change", function () {
      var f = input.files && input.files[0];
      if (!f || !/^image\//.test(f.type)) return;
      var reader = new FileReader();
      reader.onload = function () { img.src = reader.result; img.hidden = false; };
      reader.readAsDataURL(f);
    });
  });

  if (form && form.hasAttribute("data-char-counter")) {
    $$("input[maxlength], textarea[maxlength]", form).forEach(function (el) {
      if (el.type === "hidden" || el.closest(".empty-form") || el.hidden || +el.maxLength <= 0 || +el.maxLength > 5000) return;
      if (el.type !== "text" && el.tagName !== "TEXTAREA" && el.type !== "email" && el.type !== "url") return;
      var c = document.createElement("span");
      c.className = "cc-counter";
      var host = el.closest(".cc-color") || el;
      host.parentNode.insertBefore(c, host.nextSibling);
      var paint = function () { var n = el.value.length; c.textContent = n + " / " + el.maxLength; c.classList.toggle("is-near", n > el.maxLength * 0.9); };
      on(el, "input", paint);
      paint();
    });
  }

  function compile(expr) {
    var tokens = [], re = /\s*(?:(\d+(?:\.\d+)?)|("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')|(==|!=|>=|<=|>|<|\(|\)|\[|\]|,)|([A-Za-z_][\w]*))/y, m;
    re.lastIndex = 0;
    var src = String(expr);
    while (re.lastIndex < src.length) {
      var start = re.lastIndex;
      m = re.exec(src);
      if (!m) { if (/^\s*$/.test(src.slice(start))) break; throw new Error("bad expression"); }
      if (m[1]) tokens.push({ t: "num", v: parseFloat(m[1]) });
      else if (m[2]) tokens.push({ t: "str", v: m[2].slice(1, -1).replace(/\\(.)/g, "$1") });
      else if (m[3]) tokens.push({ t: "op", v: m[3] });
      else if (m[4]) {
        var w = m[4];
        if (w === "and" || w === "or" || w === "not" || w === "in") tokens.push({ t: "op", v: w });
        else if (w === "true" || w === "True") tokens.push({ t: "lit", v: true });
        else if (w === "false" || w === "False") tokens.push({ t: "lit", v: false });
        else if (w === "null" || w === "None") tokens.push({ t: "lit", v: null });
        else tokens.push({ t: "id", v: w });
      }
    }
    var pos = 0;
    function peek(v) { return tokens[pos] && tokens[pos].t === "op" && tokens[pos].v === v; }
    function orExpr() { var l = andExpr(); while (peek("or")) { pos++; var r = andExpr(); l = (function (a, b) { return function (c) { return a(c) || b(c); }; })(l, r); } return l; }
    function andExpr() { var l = notExpr(); while (peek("and")) { pos++; var r = notExpr(); l = (function (a, b) { return function (c) { return a(c) && b(c); }; })(l, r); } return l; }
    function notExpr() { if (peek("not")) { pos++; var e = notExpr(); return function (c) { return !e(c); }; } return cmp(); }
    function norm(x) { if (x === true || x === "on") return true; if (x === false) return false; return x; }
    function cmp() {
      var l = atom();
      var ops = ["==", "!=", ">=", "<=", ">", "<", "in"];
      for (var i = 0; i < ops.length; i++) {
        if (peek(ops[i])) {
          var op = ops[i]; pos++;
          var r = atom();
          return (function (a, b, o) {
            return function (c) {
              var x = a(c), y = b(c);
              if (o === "in") return Array.isArray(y) ? y.map(String).indexOf(String(x)) >= 0 : String(y).indexOf(String(x)) >= 0;
              if (typeof x === "boolean" || typeof y === "boolean") { x = norm(x); y = norm(y); }
              else if (typeof y === "number" || typeof x === "number") { x = parseFloat(x); y = parseFloat(y); }
              else { x = x == null ? "" : String(x); y = y == null ? "" : String(y); }
              if (o === "==") return x === y; if (o === "!=") return x !== y;
              if (o === ">") return x > y; if (o === "<") return x < y; if (o === ">=") return x >= y; return x <= y;
            };
          })(l, r, op);
        }
      }
      return l;
    }
    function atom() {
      var tk = tokens[pos++];
      if (!tk) throw new Error("unexpected end");
      if (tk.t === "num" || tk.t === "str" || tk.t === "lit") return function () { return tk.v; };
      if (tk.t === "id") return function (c) { var v = c[tk.v]; if (Array.isArray(v)) return v; return v === undefined ? "" : v; };
      if (tk.t === "op" && tk.v === "(") { var e = orExpr(); pos++; return e; }
      if (tk.t === "op" && tk.v === "[") {
        var parts = [];
        while (!peek("]")) { parts.push(atom()); if (peek(",")) pos++; }
        pos++;
        return function (c) { return parts.map(function (p) { return p(c); }); };
      }
      throw new Error("unexpected token");
    }
    var fn = orExpr();
    return function (ctx) {
      var v = fn(ctx);
      if (Array.isArray(v)) return v.length > 0;
      return v !== "" && v !== false && v !== null && v !== undefined && v !== 0 && v !== "0";
    };
  }

  function sortable(group) {
    var field = group.dataset.orderField;
    var dragging = null;
    function items() {
      return $$(group.dataset.inlineType === "tabular" ? "tbody > tr.form-row:not(.empty-form)" : ".inline-related:not(.empty-form)", group);
    }
    function renumber() {
      items().forEach(function (it, i) {
        var input = $('input[name$="-' + field + '"]', it);
        if (input && String(input.value) !== String(i + 1)) { input.value = i + 1; input.dispatchEvent(new Event("change", { bubbles: true })); }
      });
    }
    function wire() {
      items().forEach(function (it) {
        if (it.dataset.ccDrag) return;
        it.dataset.ccDrag = "1";
        var handle = $("[data-drag]", it);
        if (!handle) return;
        on(handle, "mousedown", function () { it.draggable = true; });
        on(handle, "touchstart", function () { it.draggable = true; }, { passive: true });
        on(it, "dragstart", function (e) { dragging = it; it.classList.add("is-dragging"); e.dataTransfer.effectAllowed = "move"; try { e.dataTransfer.setData("text/plain", ""); } catch (x) {} });
        on(it, "dragend", function () { it.draggable = false; it.classList.remove("is-dragging"); $$(".is-drop-target", group).forEach(function (t) { t.classList.remove("is-drop-target"); }); dragging = null; renumber(); });
        on(it, "dragover", function (e) {
          if (!dragging || dragging === it) return;
          e.preventDefault();
          var r = it.getBoundingClientRect();
          var after = e.clientY > r.top + r.height / 2;
          it.parentNode.insertBefore(dragging, after ? it.nextSibling : it);
        });
      });
    }
    wire();
    new MutationObserver(wire).observe(group, { childList: true, subtree: true });
    on(group.closest("form"), "submit", renumber);
  }

  function initCharts(ctx) {
  $$(".cc-chart-line[data-chart]", ctx).forEach(function (chart) {
    var data;
    try { data = JSON.parse(chart.dataset.chart); } catch (e) { return; }
    var plot = $(".cc-chart-plot", chart);
    var cursorLine = $(".cc-chart-cursor", chart);
    var top = parseFloat(chart.dataset.top) || 1;
    var stacked = chart.dataset.stacked === "1";
    var tip = document.createElement("div");
    tip.className = "cc-chart-tip";
    tip.hidden = true;
    plot.appendChild(tip);
    var dots = data.series.map(function (s) { var d = document.createElement("span"); d.className = "cc-chart-dot"; d.style.background = s.color; d.hidden = true; plot.appendChild(d); return d; });
    var n = Math.max(data.labels.length, data.series.reduce(function (m, s) { return Math.max(m, s.values.length); }, 0));
    function fmt(v) {
      var a = Math.abs(v), unit = "", x = v;
      if (a >= 1e9) { x = v / 1e9; unit = "B"; } else if (a >= 1e6) { x = v / 1e6; unit = "M"; } else if (a >= 1e4) { x = v / 1e3; unit = "k"; }
      var txt = unit ? (Math.round(x * 10) / 10).toString() : Math.round(x * 100) / 100 === Math.round(x) ? Math.round(x).toLocaleString() : (Math.round(x * 100) / 100).toLocaleString();
      return (data.prefix || "") + txt + unit + (data.suffix || "");
    }
    on(plot, "mousemove", function (e) {
      var r = plot.getBoundingClientRect();
      var i = n === 1 ? 0 : Math.round((e.clientX - r.left) / r.width * (n - 1));
      i = Math.max(0, Math.min(n - 1, i));
      var x = n === 1 ? r.width / 2 : i / (n - 1) * r.width;
      cursorLine.style.left = x + "px";
      cursorLine.style.opacity = 1;
      var running = 0, minY = r.height;
      var rowsHtml = data.series.map(function (s, k) {
        var v = s.values[i] || 0;
        running += v;
        var y = r.height - (stacked ? running : v) / top * r.height;
        minY = Math.min(minY, y);
        dots[k].hidden = false;
        dots[k].style.left = x + "px";
        dots[k].style.top = y + "px";
        return '<div><span><i style="background:' + s.color + '"></i>' + esc(s.name || "Value") + "</span><em>" + esc(fmt(v)) + "</em></div>";
      }).join("");
      tip.innerHTML = "<b>" + esc(data.labels[i] || "") + "</b>" + rowsHtml;
      tip.hidden = false;
      var left = Math.max(70, Math.min(r.width - 70, x));
      tip.style.left = left + "px";
      tip.style.top = Math.max(minY, 30) + "px";
    });
    on(plot, "mouseleave", function () { tip.hidden = true; cursorLine.style.opacity = 0; dots.forEach(function (d) { d.hidden = true; }); });
  });
  $$(".cc-chart-bar[data-chart]", ctx).forEach(function (chart) {
    var data;
    try { data = JSON.parse(chart.dataset.chart); } catch (e) { return; }
    var plot = $(".cc-chart-plot", chart);
    var tip = document.createElement("div");
    tip.className = "cc-chart-tip";
    tip.hidden = true;
    plot.appendChild(tip);
    $$(".cc-bar", chart).forEach(function (bar) {
      on(bar, "mouseenter", function () {
        var i = +bar.dataset.i;
        tip.innerHTML = "<b>" + esc(data.labels[i] || "") + "</b>" + data.series.map(function (s) {
          return '<div><span><i style="background:' + s.color + '"></i>' + esc(s.name || "Value") + "</span><em>" + esc((data.prefix || "") + (s.values[i] || 0).toLocaleString() + (data.suffix || "")) + "</em></div>";
        }).join("");
        var pr = plot.getBoundingClientRect(), br = bar.getBoundingClientRect();
        var tallest = Math.min.apply(null, $$("i", bar).map(function (x) { return x.getBoundingClientRect().top; }));
        tip.style.left = Math.max(70, Math.min(pr.width - 70, br.left - pr.left + br.width / 2)) + "px";
        tip.style.top = Math.max(30, tallest - pr.top) + "px";
        tip.hidden = false;
      });
      on(bar, "mouseleave", function () { tip.hidden = true; });
    });
  });
  $$(".cc-donut", ctx).forEach(function (d) {
    var center = $(".cc-donut-center", d);
    if (!center) return;
    var orig = center.innerHTML;
    $$("circle[data-label]", d).forEach(function (c) {
      on(c, "mouseenter", function () {
        center.innerHTML = "<b>" + esc(c.dataset.value) + "</b><span>" + esc(c.dataset.label) + "</span>";
        $$("circle[data-label]", d).forEach(function (o) { o.style.opacity = o === c ? 1 : 0.35; });
      });
      on(c, "mouseleave", function () { center.innerHTML = orig; $$("circle[data-label]", d).forEach(function (o) { o.style.opacity = ""; }); });
    });
  });
  }
  initCharts();

  on(document, "keydown", function (e) {
    if (e.key !== "Escape" || recording) return;
    if (typing(e) && !anyDialogOpen()) { e.target.blur(); return; }
    closeMenus();
    setSide(false);
  });

  var sc = config.shortcuts || {};
  var keyOverrides = sc.editable ? store.get("keys", {}) : {};
  var KEYNAMES = { mod: isMac ? "⌘" : "Ctrl", alt: isMac ? "⌥" : "Alt", shift: isMac ? "⇧" : "Shift", enter: "↵", escape: "Esc", arrowleft: "←", arrowright: "→", arrowup: "↑", arrowdown: "↓", space: "Space", backspace: "⌫", "delete": "Del", plus: "+", tab: "Tab", pageup: "PgUp", pagedown: "PgDn" };
  function keyName(p) { return KEYNAMES[p] || (p.length === 1 ? p.toUpperCase() : p.charAt(0).toUpperCase() + p.slice(1)); }
  function keyHtml(seq) {
    return seq.split(" ").map(function (step) {
      return '<span class="cc-combo">' + step.split("+").map(function (p) { return "<kbd>" + esc(keyName(p)) + "</kbd>"; }).join("") + "</span>";
    }).join('<span class="cc-then">then</span>');
  }
  function keyText(seq) {
    return seq.split(" ").map(function (step) { return step.split("+").map(keyName).join(isMac ? "" : "+"); }).join(" ");
  }
  function actions() { return sc.actions || []; }
  function actionById(id) { return actions().filter(function (a) { return a.id === id; })[0]; }
  function actionKeys(a) { return keyOverrides[a.id] || a.keys || []; }
  function comboOf(e) {
    var k = e.key;
    if (!k || k === "Dead" || k === "Unidentified" || /^(Control|Meta|Shift|Alt|OS|AltGraph|CapsLock)$/.test(k)) return "";
    if (e.altKey && /^Key[A-Z]$/.test(e.code || "")) k = e.code.slice(3);
    if (e.altKey && /^Digit\d$/.test(e.code || "")) k = e.code.slice(5);
    k = k === " " ? "space" : k === "+" ? "plus" : k.toLowerCase();
    var parts = [];
    if (e.metaKey || e.ctrlKey) parts.push("mod");
    if (e.altKey) parts.push("alt");
    if (e.shiftKey && (k.length > 1 || /[a-z0-9]/.test(k))) parts.push("shift");
    parts.push(k);
    return parts.join("+");
  }
  function scopeActive(scope) { return scope === "global" || scope === "custom" || (scope === "list" && !!changelist) || (scope === "form" && !!form); }
  function lookup(seq) {
    var hits = [], prefix = false;
    actions().forEach(function (a) {
      if (!scopeActive(a.scope)) return;
      actionKeys(a).forEach(function (k) {
        if (k === seq) hits.push(a);
        else if (k.indexOf(seq + " ") === 0) prefix = true;
      });
    });
    hits.sort(function (a, b) { return (a.scope === "global" ? 1 : 0) - (b.scope === "global" ? 1 : 0); });
    return { hits: hits, prefix: prefix };
  }
  function go(url, newTab) { if (!url) return false; if (newTab) window.open(url, "_blank"); else location.href = url; }
  function clickEl(el) { if (!el) return false; el.click(); }
  function hrefOf(sel) { var el = $(sel); return el ? el.getAttribute("href") : ""; }
  function cycleTab(step) {
    var buttons = $$("[data-tabs] [data-tab]");
    if (!buttons.length) return false;
    var i = buttons.findIndex(function (b) { return b.classList.contains("is-active"); });
    buttons[(i + step + buttons.length) % buttons.length].click();
  }
  var handlers = {
    palette: function () { if (!config.palette) return false; palette.open(); },
    help: function () { openKeys(); },
    search: function () { var s = $("#searchbar") || $("[data-nav-filter]"); if (!s) return false; s.focus(); s.select(); },
    dashboard: function () { return go(hrefOf(".cc-nav-root [data-nav-item]")); },
    activity: function () { return go(config.activity); },
    site: function () { return go(config.site); },
    theme: function () { if (!config.switcher) return false; syncPanel(); openDialog($("[data-theme-panel]")); },
    menu: function () { toggleCollapse(); },
    next_row: function () { setCursor(cursor + 1); },
    prev_row: function () { setCursor(cursor - 1); },
    select_row: function () { if (cursor < 0) return false; return clickEl($("input.action-select", rows()[cursor])); },
    select_all: function () { return clickEl($("#action-toggle")); },
    open_row: function () { if (cursor < 0) return false; openRow(false); },
    open_row_tab: function () { if (cursor < 0) return false; openRow(true); },
    expand_row: function () { if (cursor < 0) return false; return clickEl($("[data-expand]", rows()[cursor])); },
    add: function () { return go(hrefOf("[data-shortcut-add]")); },
    filters: function () { return clickEl($('[data-drawer-open="filters"]')); },
    columns: function () { var m = $("[data-columns-menu]:not([hidden]) [data-menu-toggle]"); return clickEl(m); },
    "export": function () { return clickEl($("[data-export-menu] [data-menu-toggle]")); },
    prev_page: function () { return go(hrefOf("[data-page-prev]")); },
    next_page: function () { return go(hrefOf("[data-page-next]")); },
    save: function () { return clickEl($("[data-save]", form) || $("[data-save-continue]", form)); },
    save_continue: function () { return clickEl($("[data-save-continue]", form) || $("[data-save]", form)); },
    save_add: function () { return clickEl($('button[name="_addanother"]', form)); },
    next_tab: function () { return cycleTab(1); },
    prev_tab: function () { return cycleTab(-1); },
    history: function () { return go(hrefOf(".historylink")); },
    back: function () { return go(hrefOf("[data-back-link]") || hrefOf(".breadcrumbs li:nth-last-child(2) a")); },
    "delete": function () { return go(hrefOf(".deletelink")); }
  };
  function runAction(a, e) {
    var result;
    if (handlers[a.id]) result = handlers[a.id](e);
    else if (a.click) result = clickEl($(a.click));
    else if (a.url) result = go(a.url, a.new_tab);
    else result = false;
    return result !== false;
  }
  var buffer = "", bufferTimer = null, bufferHit = null;
  function clearBuffer() { buffer = ""; bufferHit = null; clearTimeout(bufferTimer); }
  on(document, "keydown", function (e) {
    if (!sc.enabled || recording || e.defaultPrevented || e.isComposing) return;
    var combo = comboOf(e);
    if (!combo) return;
    var hasMod = combo.indexOf("mod+") === 0;
    if (anyDialogOpen() && !hasMod) return;
    if (typing(e) && !hasMod) return;
    var seq = buffer ? buffer + " " + combo : combo;
    var found = lookup(seq);
    if (!found.hits.length && !found.prefix && buffer) { clearBuffer(); seq = combo; found = lookup(seq); }
    if (!found.hits.length && !found.prefix) { clearBuffer(); return; }
    if (found.prefix) {
      e.preventDefault();
      clearTimeout(bufferTimer);
      buffer = seq;
      bufferHit = found.hits[0] || null;
      bufferTimer = setTimeout(function () { var hit = bufferHit; clearBuffer(); if (hit) runAction(hit); }, 800);
      return;
    }
    clearBuffer();
    for (var i = 0; i < found.hits.length; i++) {
      if (runAction(found.hits[i], e)) { e.preventDefault(); return; }
    }
  });

  function fillKbd() {
    $$("kbd[data-shortcut]").forEach(function (k) {
      var a = actionById(k.dataset.shortcut);
      var keys = a && sc.enabled ? actionKeys(a) : [];
      k.hidden = !keys.length;
      if (keys.length) k.textContent = keyText(keys[0]);
    });
  }
  function openKeys() { renderKeys(); openDialog($("[data-keys]")); }
  function renderKeys() {
    var body = $("[data-keys-body]");
    if (!body) return;
    var groups = {};
    actions().forEach(function (a) { (groups[a.scope] = groups[a.scope] || []).push(a); });
    body.innerHTML = ["global", "list", "form", "custom"].filter(function (g) { return groups[g]; }).map(function (g) {
      return "<section><h3>" + esc((sc.scopes || {})[g] || g) + "</h3><dl>" + groups[g].map(function (a) {
        var keys = actionKeys(a);
        var inner = keys.length ? keys.map(keyHtml).join('<span class="cc-or">or</span>') : '<em class="cc-key-off">off</em>';
        var tag = sc.editable ? 'button type="button" data-key-edit="' + esc(a.id) + '" title="Change"' : "span";
        return "<div><dt>" + esc(a.label) + '</dt><dd><' + tag + ' class="cc-key' + (keyOverrides[a.id] ? " is-custom" : "") + '">' + inner + "</" + (sc.editable ? "button" : "span") + "></dd></div>";
      }).join("") + "</dl></section>";
    }).join("");
    var reset = $("[data-keys-reset]");
    if (reset) reset.hidden = !Object.keys(keyOverrides).length;
    var hint = $("[data-keys-hint]");
    if (hint && !sc.editable) hint.hidden = true;
  }
  var recording = null;
  function saveKeys() { store.set("keys", keyOverrides); renderKeys(); fillKbd(); }
  function stopRecording() { if (!recording) return; clearTimeout(recording.timer); recording = null; }
  function finishRecording() {
    if (!recording) return;
    var rec = recording;
    stopRecording();
    if (!rec.steps.length) { renderKeys(); return; }
    var seq = rec.steps.join(" ");
    var me = actionById(rec.id);
    actions().forEach(function (other) {
      if (other.id === rec.id) return;
      var shared = other.scope === me.scope || other.scope === "global" || me.scope === "global" || other.scope === "custom" || me.scope === "custom";
      if (!shared) return;
      var ks = actionKeys(other);
      if (ks.indexOf(seq) >= 0) {
        keyOverrides[other.id] = ks.filter(function (k) { return k !== seq; });
        toast("Taken from “" + other.label + "”");
      }
    });
    if (JSON.stringify([seq]) === JSON.stringify(me.default)) delete keyOverrides[rec.id];
    else keyOverrides[rec.id] = [seq];
    saveKeys();
  }
  on(document, "click", function (e) {
    var off = e.target.closest("[data-key-off]");
    var def = e.target.closest("[data-key-default]");
    if (off || def) {
      e.preventDefault();
      var id = (off || def).closest("[data-key-edit]").dataset.keyEdit;
      stopRecording();
      if (off) keyOverrides[id] = []; else delete keyOverrides[id];
      saveKeys();
      return;
    }
    var b = e.target.closest("[data-key-edit]");
    if (b) {
      if (recording && recording.id === b.dataset.keyEdit) return;
      stopRecording();
      renderKeys();
      b = $('[data-key-edit="' + b.dataset.keyEdit + '"]');
      recording = { id: b.dataset.keyEdit, steps: [], el: b, timer: null };
      b.classList.add("is-recording");
      b.innerHTML = '<span class="cc-rec">Press keys…</span><span class="cc-rec-tools"><a href="#" data-key-off>off</a><a href="#" data-key-default>default</a></span>';
      return;
    }
    if (e.target.closest("[data-keys-reset]")) { stopRecording(); keyOverrides = {}; saveKeys(); toast("Shortcuts reset"); return; }
    if (recording && !e.target.closest("[data-key-edit]")) { stopRecording(); renderKeys(); }
  });
  document.addEventListener("keydown", function (e) {
    if (!recording) return;
    e.preventDefault();
    e.stopPropagation();
    if (e.key === "Escape" && !recording.steps.length) { stopRecording(); renderKeys(); return; }
    var c = comboOf(e);
    if (!c) return;
    recording.steps.push(c);
    clearTimeout(recording.timer);
    recording.el.innerHTML = keyHtml(recording.steps.join(" ")) + '<span class="cc-rec-dots"></span>';
    if (recording.steps.length >= 2 || c.indexOf("+") > 0) { recording.timer = setTimeout(finishRecording, 250); return; }
    recording.timer = setTimeout(finishRecording, 900);
  }, true);
  on($("[data-keys]"), "close", function () { stopRecording(); });
  fillKbd();

  function tidyLegacyCollapse() {
    $$(".cc-fieldset .collapse-toggle").forEach(function (a) {
      var h = a.closest("h2, h3, h4");
      a.remove();
      if (h) h.innerHTML = h.innerHTML.replace(/\s*\(\s*\)\s*$/, "");
    });
    $$(".cc-fieldset.collapsed").forEach(function (f) { f.classList.remove("collapsed"); });
  }
  tidyLegacyCollapse();
  on(window, "load", tidyLegacyCollapse);

  var audio = null;
  function audioCtx() {
    var A = window.AudioContext || window.webkitAudioContext;
    if (!A) return null;
    if (!audio) { try { audio = new A(); } catch (e) { return null; } }
    if (audio.state === "suspended") audio.resume();
    return audio;
  }
  ["pointerdown", "keydown"].forEach(function (t) { document.addEventListener(t, function () { audioCtx(); }, { once: true, capture: true }); });
  var SOUNDS = {
    chime: [[880, 0, 0.35, "sine", 0.5], [1318.5, 0.09, 0.55, "sine", 0.35]],
    pop: [[420, 0, 0.1, "sine", 0.7, 920]],
    ping: [[1760, 0, 0.3, "triangle", 0.35]],
    bell: [[660, 0, 1.1, "sine", 0.45], [1320, 0, 0.7, "sine", 0.16], [1980, 0, 0.45, "sine", 0.07]],
    alert: [[880, 0, 0.13, "square", 0.16], [660, 0.16, 0.13, "square", 0.16], [880, 0.32, 0.2, "square", 0.16]],
    sparkle: [[1046.5, 0, 0.18, "sine", 0.3], [1318.5, 0.07, 0.18, "sine", 0.3], [1568, 0.14, 0.18, "sine", 0.3], [2093, 0.21, 0.35, "sine", 0.25]],
    blip: [[1200, 0, 0.06, "square", 0.1]],
    cash: [[1567, 0, 0.09, "triangle", 0.35], [2093, 0.09, 0.4, "triangle", 0.3]],
    knock: [[200, 0, 0.08, "sine", 0.9, 90], [200, 0.15, 0.08, "sine", 0.9, 90]]
  };
  function play(name, volume) {
    var spec = SOUNDS[name];
    var c = spec && audioCtx();
    if (!c || !(volume > 0)) return;
    var t0 = c.currentTime + 0.02;
    var master = c.createGain();
    master.gain.value = Math.min(1, volume);
    master.connect(c.destination);
    spec.forEach(function (n) {
      var o = c.createOscillator(), g = c.createGain(), at = t0 + n[1];
      o.type = n[3];
      o.frequency.setValueAtTime(n[0], at);
      if (n[5]) o.frequency.exponentialRampToValueAtTime(n[5], at + n[2]);
      g.gain.setValueAtTime(0.0001, at);
      g.gain.exponentialRampToValueAtTime(n[4], at + 0.012);
      g.gain.exponentialRampToValueAtTime(0.0001, at + n[2]);
      o.connect(g);
      g.connect(master);
      o.start(at);
      o.stop(at + n[2] + 0.05);
    });
  }

  var N = config.notify || {}, P = config.push || {}, L = config.live || {};
  var ns = {};
  (function () {
    var saved = store.get("notify", {}) || {};
    ns = { popup: true, sound: N.sound !== "none", tone: "", volume: typeof N.volume === "number" ? N.volume : 0.6, desktop: false, dnd: 0, live: true };
    Object.keys(saved).forEach(function (k) { ns[k] = saved[k]; });
  })();
  function saveNs() { store.set("notify", ns); }
  function quiet() { return ns.dnd && Date.now() < ns.dnd; }
  function post(url, body, json) {
    var headers = { "X-CSRFToken": csrf(), "X-Requested-With": "XMLHttpRequest" };
    if (json) headers["Content-Type"] = "application/json";
    return fetch(url, { method: "POST", credentials: "same-origin", headers: headers, body: json ? JSON.stringify(body) : body });
  }
  function ensureIcon(name, svg) {
    if (!name || !svg || document.getElementById("cc-i-" + name)) return;
    var sprite = $("svg.cc-sprite");
    if (sprite) sprite.insertAdjacentHTML("beforeend", svg);
  }
  function since(at) { var t = Date.parse(at); return isNaN(t) ? "" : ago(t); }

  var bell = $("[data-bell]");
  var bellCount = $("[data-bell-count]");
  var baseTitle = document.title;
  function setUnread(n) {
    if (bellCount) { bellCount.hidden = !n; bellCount.textContent = n > 99 ? "99+" : n; }
    if (bell) bell.classList.toggle("has-unread", n > 0);
    document.title = (n ? "(" + (n > 99 ? "99+" : n) + ") " : "") + baseTitle;
  }
  setUnread(N.unread || 0);
  var bellFilter = "all", bellLoaded = false;
  function noteHtml(n) {
    return '<a class="cc-ntf' + (n.read ? "" : " is-unread") + '" href="' + esc(n.link || "#") + '" data-note="' + n.id + '"><span class="cc-ntf-icon cc-tone-' + esc(n.level) + '">' + icon(n.icon) + '</span><span class="cc-ntf-text"><b>' + esc(n.title) + "</b>" + (n.body ? "<small>" + esc(n.body) + "</small>" : "") + "<time>" + esc((n.actor ? n.actor + " · " : "") + since(n.at)) + '</time></span><i class="cc-ntf-dot"></i></a>';
  }
  function renderBell(items) {
    var list = $("[data-bell-list]");
    if (!list) return;
    items.forEach(function (n) { ensureIcon(n.icon, n.svg); });
    list.innerHTML = items.length ? items.map(noteHtml).join("") : '<div class="cc-bell-empty">' + icon("bell") + "<span>" + (bellFilter === "unread" ? "Nothing unread. Nice." : "No notifications yet.") + "</span></div>";
  }
  function loadBell() {
    if (!N.list) return;
    fetch(N.list + "?format=json" + (bellFilter === "unread" ? "&filter=unread" : ""), { credentials: "same-origin" })
      .then(function (r) { return r.json(); })
      .then(function (d) { bellLoaded = true; renderBell(d.items || []); setUnread(d.unread || 0); })
      .catch(function () {});
  }
  function markRead(ids) {
    if (!N.read) return;
    var body = new URLSearchParams();
    (ids || []).forEach(function (id) { body.append("id", id); });
    post(N.read, body).then(function (r) { return r.json(); }).then(function (d) { setUnread(d.unread || 0); }).catch(function () {});
    $$(ids ? ids.map(function (id) { return '[data-note="' + id + '"]'; }).join(",") : "[data-note]").forEach(function (el) { el.classList.remove("is-unread"); });
  }
  on(document, "click", function (e) {
    if (e.target.closest("[data-bell] [data-menu-toggle]")) { setTimeout(function () { if (bell && bell.classList.contains("is-open")) loadBell(); }, 0); return; }
    var f = e.target.closest("[data-bell-filter] [data-value]");
    if (f) { bellFilter = f.dataset.value; $$("[data-bell-filter] [data-value]").forEach(function (b) { b.classList.toggle("is-on", b === f); }); loadBell(); return; }
    if (e.target.closest("[data-bell-readall]")) { markRead(null); return; }
    var note = e.target.closest("[data-note]");
    if (note) {
      if (note.classList.contains("is-unread")) markRead([note.dataset.note]);
      if (note.getAttribute("href") === "#") e.preventDefault();
    }
  });

  var pops = $("[data-pops]");
  var LEVEL_SOUND = N.sounds || {};
  function dropPop(el) {
    if (!el || el.classList.contains("is-out")) return;
    el.classList.add("is-out");
    setTimeout(function () { el.remove(); }, 280);
  }
  function popup(n) {
    if (!pops) return;
    var dur = +N.duration || 0;
    var el = document.createElement("div");
    el.className = "cc-pop cc-tone-" + (n.level || "info");
    el.setAttribute("role", "status");
    el.innerHTML = '<span class="cc-pop-icon">' + icon(n.icon) + '</span><div class="cc-pop-text"><b>' + esc(n.title) + "</b>" + (n.body ? "<p>" + esc(n.body) + "</p>" : "") + "<small>" + esc((n.actor ? n.actor + " · " : "") + "just now") + "</small>" + (n.link ? '<span class="cc-pop-actions"><a href="' + esc(n.link) + '" data-pop-open>Open</a><button type="button" data-pop-read>Mark read</button></span>' : '<span class="cc-pop-actions"><button type="button" data-pop-read>Mark read</button></span>') + '</div><button type="button" class="cc-icon-btn cc-pop-close" data-pop-close aria-label="Close">' + icon("x") + "</button>" + (dur ? '<i class="cc-pop-timer" style="animation-duration:' + dur + 's"></i>' : "");
    var top = /^top/.test(pops.dataset.position || "");
    if (top) pops.insertBefore(el, pops.firstChild); else pops.appendChild(el);
    var all = $$(".cc-pop:not(.is-out)", pops);
    var max = N.max || 4;
    while (all.length > max) dropPop(top ? all.pop() : all.shift());
    requestAnimationFrame(function () { el.classList.add("is-in"); });
    var left = dur * 1000, started = Date.now(), timer = dur ? setTimeout(function () { dropPop(el); }, left) : null;
    on(el, "mouseenter", function () { if (!timer) return; clearTimeout(timer); timer = null; left -= Date.now() - started; el.classList.add("is-paused"); });
    on(el, "mouseleave", function () { if (!dur || timer || el.classList.contains("is-out")) return; started = Date.now(); el.classList.remove("is-paused"); timer = setTimeout(function () { dropPop(el); }, Math.max(800, left)); });
    on(el, "click", function (e) {
      if (e.target.closest("[data-pop-close]")) { dropPop(el); return; }
      if (e.target.closest("[data-pop-read]")) { markRead([n.id]); dropPop(el); return; }
      if (e.target.closest("[data-pop-open]")) { markRead([n.id]); return; }
      if (n.link && !e.target.closest("a, button")) { markRead([n.id]); location.href = n.link; }
    });
  }
  var pushOn = false;
  function desktop(n) {
    if (!ns.desktop || !N.desktop || pushOn || !("Notification" in window) || Notification.permission !== "granted") return;
    if (N.desktopWhen !== "always" && !document.hidden) return;
    try {
      var d = new Notification(n.title, { body: n.body || "", tag: "cc-" + n.id, icon: P.icon || undefined });
      d.onclick = function () { window.focus(); if (n.link) location.href = n.link; markRead([n.id]); d.close(); };
    } catch (e) {}
  }
  var seen = {};
  function receive(list) {
    var heard = store.get("heard", 0) || 0;
    var loudest = null;
    list.forEach(function (n) {
      if (seen[n.id]) return;
      seen[n.id] = 1;
      ensureIcon(n.icon, n.svg);
      var listEl = $("[data-bell-list]");
      if (bellLoaded && listEl && bellFilter !== "read") {
        var empty = $(".cc-bell-empty", listEl);
        if (empty) empty.remove();
        listEl.insertAdjacentHTML("afterbegin", noteHtml(n));
      }
      if (bell) { bell.classList.remove("is-ringing"); void bell.offsetWidth; bell.classList.add("is-ringing"); }
      var fresh = n.id > heard;
      if (fresh) { heard = n.id; store.set("heard", n.id); }
      if (quiet()) return;
      if (ns.popup && N.popup && !document.hidden) popup(n);
      if (fresh) { desktop(n); loudest = loudest || n; }
    });
    if (loudest && ns.sound && !quiet()) play(ns.tone || loudest.sound || LEVEL_SOUND[loudest.level] || N.sound, ns.volume);
  }

  $$("[data-announce]").forEach(function (a) {
    if (store.get("ann:" + a.dataset.announce, 0)) { a.remove(); return; }
    if (a.dataset.announceStyle === "modal") setTimeout(function () { if (!anyDialogOpen()) a.showModal(); }, 500);
    else a.hidden = false;
  });
  on(document, "click", function (e) {
    var c = e.target.closest("[data-announce-close]");
    if (!c) return;
    var a = c.closest("[data-announce]");
    store.set("ann:" + a.dataset.announce, 1);
    if (a.tagName === "DIALOG") a.close(); else a.remove();
  });

  var liveOn = !!(L.enabled && ns.live !== false);
  var liveDot = $("[data-live-dot]");
  function liveState(state) {
    if (liveDot) { liveDot.dataset.state = state; liveDot.title = state === "on" ? "Live updates on" : state === "paused" ? "Live updates paused" : "Reconnecting…"; }
    var t = $("[data-live-state]");
    if (t) t.textContent = state === "on" ? "Connected. Lists, dashboards and badges refresh on their own." : state === "paused" ? "Paused in this browser." : "Trying to reconnect…";
  }
  var noteSince = N.since || 0;
  var versions = {};
  $$("[data-live-model]").forEach(function (el) { versions[el.dataset.liveModel] = el.dataset.liveVersion || ""; });
  var dashEl = $("[data-live-dashboard]");
  if (dashEl) versions["*"] = dashEl.dataset.liveVersion || "";
  var objEl = $("[data-live-object]");
  var objKey = objEl ? objEl.dataset.liveObject : "";
  var needBadges = false, badgesAt = Date.now();
  function liveParams(badges) {
    var p = { since: noteSince, mode: dirty ? "editing" : "viewing" };
    var m = Object.keys(versions).map(function (k) { return k + "=" + versions[k]; }).join(",");
    if (m) p.models = m;
    if (objKey) p.object = objKey;
    if (badges) p.badges = "1";
    return p;
  }
  function qs(p) { return Object.keys(p).map(function (k) { return encodeURIComponent(k) + "=" + encodeURIComponent(p[k]); }).join("&"); }
  function applyBadges(map) {
    Object.keys(map).forEach(function (key) {
      $$('[data-badge-key="' + key.replace(/"/g, '\\"') + '"]').forEach(function (b) {
        var v = map[key];
        if (b.textContent !== v && v) { b.classList.remove("is-bumped"); void b.offsetWidth; b.classList.add("is-bumped"); }
        b.textContent = v;
        b.hidden = !v || v === "0";
      });
    });
  }
  function showPresence(list) {
    var box = $("[data-presence]");
    if (!box) return;
    box.hidden = !list.length;
    box.innerHTML = list.map(function (p) {
      return '<span class="cc-presence-who' + (p.mode === "editing" ? " is-editing" : "") + '" title="' + esc(p.name + (p.mode === "editing" ? " is editing" : " is viewing")) + '"><span class="cc-avatar" data-seed="' + esc(p.username) + '">' + esc(initials(p.name)) + "</span></span>";
    }).join("") + (list.length ? "<small>" + esc(list.length === 1 ? list[0].name.split(" ")[0] + (list[0].mode === "editing" ? " is editing this too" : " is looking at this too") : list.length + " others are here") + "</small>" : "");
    paintAvatars(box);
  }
  function initials(name) { return String(name || "?").split(/\s+/).slice(0, 2).map(function (w) { return w.charAt(0); }).join("").toUpperCase(); }
  function objectChanged(info) {
    var parts = objKey.split(":");
    parts[2] = info.log;
    objKey = parts.join(":");
    var old = $("[data-live-note]");
    if (old) old.remove();
    var note = document.createElement("div");
    note.className = "cc-live-note cc-tone-" + (info.deleted ? "danger" : "warning");
    note.setAttribute("data-live-note", "");
    note.innerHTML = icon(info.deleted ? "trash" : "refresh-cw") + "<p><b>" + esc(info.who || "Someone") + "</b> " + (info.deleted ? "deleted this record" : "saved this record") + " " + esc(info.ago) + "." + (info.message ? " <span>" + esc(info.message) + "</span>" : "") + "</p>" + (info.deleted ? "" : '<a href="' + esc(location.href) + '" class="cc-btn cc-btn-sm">Reload</a>') + '<button type="button" class="cc-icon-btn" aria-label="Dismiss">' + icon("x") + "</button>";
    on($("button", note), "click", function () { note.remove(); });
    var host = $(".cc-pagehead") || $("#content");
    host.parentNode.insertBefore(note, host.nextSibling);
    if (!quiet() && ns.sound) play("knock", ns.volume * 0.8);
  }

  var listTimer = null;
  function rowKey(tr) {
    var cb = $("input.action-select", tr);
    if (cb) return "pk:" + cb.value;
    var a = $("th a, td a", tr);
    return a ? a.getAttribute("href") : tr.textContent.trim().slice(0, 80);
  }
  function listBusy() {
    return $$("input.action-select:checked").length || $("#action-toggle:checked") || $("[data-menu].is-open") || anyDialogOpen() || $("tr.is-dragging") || $("#result_list input:not([type=checkbox]), #result_list select, #result_list textarea") || $("tr.is-expanded");
  }
  function listBanner() {
    if (!changelist || $("[data-live-bar]")) return;
    var bar = document.createElement("div");
    bar.className = "cc-live-bar";
    bar.setAttribute("data-live-bar", "");
    bar.innerHTML = '<span class="cc-live-pulse"></span><span>This list has new changes.</span><button type="button" class="cc-btn cc-btn-sm cc-btn-primary">Show</button>';
    on($("button", bar), "click", function () { bar.remove(); swapList(true); });
    var tools = $(".cc-list-toolbar", changelist);
    changelist.insertBefore(bar, tools ? tools.nextSibling : changelist.firstChild);
  }
  function swapList(force) {
    if (!changelist) return;
    if (!force && (L.lists === "banner" || listBusy())) { listBanner(); return; }
    fetch(location.href, { credentials: "same-origin", headers: { "X-Requested-With": "XMLHttpRequest" } })
      .then(function (r) { return r.text(); })
      .then(function (html) {
        var doc = new DOMParser().parseFromString(html, "text/html");
        var freshBody = doc.querySelector("#result_list tbody");
        var oldBody = results && $("tbody", results);
        if (!freshBody || !oldBody || !$("#result_list thead") || doc.querySelectorAll("#result_list thead th").length !== $$("#result_list thead th").length) { location.reload(); return; }
        var before = {};
        $$("tr[data-row]", oldBody).forEach(function (tr) { before[rowKey(tr)] = tr.innerHTML.replace(/\s+/g, " "); });
        $$("svg use", freshBody).forEach(function (u) { var id = (u.getAttribute("href") || "").slice(1); if (id && !document.getElementById(id)) { var sym = doc.getElementById(id); if (sym) ensureIcon(id.replace("cc-i-", ""), sym.outerHTML); } });
        oldBody.innerHTML = freshBody.innerHTML;
        var added = 0, changedRows = 0;
        $$("tr[data-row]", oldBody).forEach(function (tr) {
          var k = rowKey(tr);
          if (!(k in before)) { added++; if (L.highlight) tr.classList.add("is-live-new"); }
          else if (before[k] !== tr.innerHTML.replace(/\s+/g, " ")) { changedRows++; if (L.highlight) tr.classList.add("is-live-changed"); }
        });
        [".cc-lead", ".cc-pager", ".cc-tabs-page", ".cc-chips"].forEach(function (sel) {
          var a = $(sel), b = doc.querySelector(sel);
          if (a && b && a.innerHTML !== b.innerHTML) a.innerHTML = b.innerHTML;
        });
        applyCols();
        wireSort();
        paintAvatars(oldBody);
        if (window.Actions && $$("tr input.action-select").length) { try { window.Actions(document.querySelectorAll("tr input.action-select")); } catch (e) {} }
        if (typeof updateActionbar === "function") updateActionbar();
        var bar = $("[data-live-bar]");
        if (bar) bar.remove();
        if (added || changedRows) toast(added ? added + (added === 1 ? " new row" : " new rows") : changedRows + (changedRows === 1 ? " row updated" : " rows updated"));
      })
      .catch(function () {});
  }
  var dashAt = 0, dashTimer = null;
  function strip(html) { return html.replace(/cc-g\d+/g, "g").replace(/\s+/g, " "); }
  function refreshDashboard() {
    if (!dashEl || !L.dashboard) return;
    var wait = dashAt + L.dashboardInterval * 1000 - Date.now();
    if (wait > 0) { clearTimeout(dashTimer); dashTimer = setTimeout(refreshDashboard, wait); return; }
    dashAt = Date.now();
    fetch(location.href, { credentials: "same-origin" })
      .then(function (r) { return r.text(); })
      .then(function (html) {
        var doc = new DOMParser().parseFromString(html, "text/html");
        var fresh = doc.querySelector("[data-live-dashboard]");
        if (!fresh) return;
        var oldKids = Array.prototype.slice.call(dashEl.children), newKids = Array.prototype.slice.call(fresh.children);
        if (oldKids.length !== newKids.length) { dashEl.innerHTML = fresh.innerHTML; initCharts(dashEl); paintAvatars(dashEl); renderRecent(dashEl); return; }
        newKids.forEach(function (kid, i) {
          if (strip(kid.innerHTML) === strip(oldKids[i].innerHTML)) return;
          var node = document.importNode(kid, true);
          node.classList.add("is-live-changed");
          oldKids[i].replaceWith(node);
          initCharts(node);
          paintAvatars(node);
          renderRecent(node);
        });
      })
      .catch(function () {});
  }
  function onVersion(label) {
    if (label === "*") { refreshDashboard(); needBadges = true; return; }
    needBadges = true;
    if (changelist && changelist.dataset.liveModel === label) { clearTimeout(listTimer); listTimer = setTimeout(function () { swapList(false); }, 250); }
  }
  function handle(data) {
    if (!data) return;
    liveState("on");
    if (data.since) noteSince = Math.max(noteSince, data.since);
    if (data.notifications && data.notifications.length) receive(data.notifications);
    if (typeof data.unread === "number") setUnread(data.unread);
    if (data.versions) Object.keys(data.versions).forEach(function (k) {
      if (k in versions && versions[k] !== data.versions[k]) { versions[k] = data.versions[k]; onVersion(k); }
    });
    if (data.object) objectChanged(data.object);
    if (data.presence) showPresence(data.presence);
    if (data.badges) applyBadges(data.badges);
  }
  function wantsBadges() {
    if (!L.badges) return false;
    if (needBadges || Date.now() - badgesAt > 60000) { needBadges = false; badgesAt = Date.now(); return true; }
    return false;
  }
  var transport = L.transport || "poll", pollTimer = null, failures = 0, source = null, socket = null, beat = null;
  function every() { return (document.hidden ? L.hidden : L.interval) * 1000; }
  function poll() {
    clearTimeout(pollTimer);
    if (!liveOn || transport !== "poll") return;
    fetch(L.poll + "?" + qs(liveParams(wantsBadges())), { credentials: "same-origin", headers: { "X-Requested-With": "XMLHttpRequest" } })
      .then(function (r) { if (!r.ok || r.redirected) throw new Error(r.status); return r.json(); })
      .then(function (d) { failures = 0; handle(d); pollTimer = setTimeout(poll, every()); })
      .catch(function () { failures++; liveState("off"); pollTimer = setTimeout(poll, Math.min(120000, every() * Math.pow(2, Math.min(failures, 5)))); });
  }
  function openStream() {
    if (source) { source.close(); source = null; }
    if (!liveOn || transport !== "sse" || !window.EventSource) return;
    source = new EventSource(L.stream + "?" + qs(liveParams(true)));
    source.onmessage = function (e) { failures = 0; try { handle(JSON.parse(e.data)); } catch (x) {} };
    source.onerror = function () {
      if (source) source.close();
      source = null;
      failures++;
      if (failures > 6) { liveState("off"); transport = "poll"; poll(); return; }
      setTimeout(openStream, failures > 1 ? 1500 * failures : 300);
    };
  }
  function syncSocket(badges) {
    if (socket && socket.readyState === 1) socket.send(JSON.stringify({ type: "sync", params: liveParams(badges || wantsBadges()) }));
  }
  function openSocket() {
    if (!liveOn || transport !== "websocket" || !window.WebSocket) return;
    var url = /^wss?:/.test(L.ws) ? L.ws : (location.protocol === "https:" ? "wss://" : "ws://") + location.host + L.ws;
    try { socket = new WebSocket(url); } catch (e) { transport = "poll"; poll(); return; }
    socket.onopen = function () { failures = 0; syncSocket(true); clearInterval(beat); beat = setInterval(function () { syncSocket(false); }, L.interval * 1000); };
    socket.onmessage = function (e) {
      var m;
      try { m = JSON.parse(e.data); } catch (x) { return; }
      if (m.type === "sync") handle(m.data);
      if (m.type === "poke") syncSocket(false);
    };
    socket.onclose = function () {
      clearInterval(beat);
      socket = null;
      if (!liveOn) return;
      failures++;
      liveState("off");
      if (failures > 4) { transport = "poll"; poll(); return; }
      setTimeout(openSocket, 1000 * failures);
    };
  }
  function startLive() {
    liveOn = !!(L.enabled && ns.live !== false);
    if (!L.enabled) return;
    if (!liveOn) { liveState("paused"); clearTimeout(pollTimer); if (source) source.close(); if (socket) socket.close(); return; }
    if (transport === "websocket") openSocket();
    else if (transport === "sse") openStream();
    else { transport = "poll"; pollTimer = setTimeout(poll, 400); }
  }
  on(document, "visibilitychange", function () {
    if (document.hidden || !liveOn) return;
    if (transport === "poll") poll();
    else if (transport === "websocket") syncSocket(true);
  });
  var wasDirty = false;
  setInterval(function () {
    if (dirty === wasDirty) return;
    wasDirty = dirty;
    if (transport === "sse") openStream();
    else if (transport === "websocket") syncSocket(false);
  }, 1000);
  startLive();

  var nsDlg = $("[data-notify-settings]");
  function nsSync() {
    if (!nsDlg) return;
    $$("[data-ns]", nsDlg).forEach(function (el) {
      var k = el.dataset.ns;
      if (el.type === "checkbox") el.checked = !!ns[k];
      else el.value = ns[k] == null ? "" : ns[k];
    });
    var box = $("[data-ns-sound-box]", nsDlg);
    if (box) box.classList.toggle("is-off", !ns.sound);
    $$("[data-ns-dnd] [data-value]", nsDlg).forEach(function (b) { b.classList.toggle("is-on", quiet() ? b.dataset.value !== "0" && b.dataset.value === String(ns.dndKind || "") : b.dataset.value === "0"); });
    var dndState = $("[data-ns-dnd-state]", nsDlg);
    if (dndState) dndState.textContent = quiet() ? "On until " + new Date(ns.dnd).toLocaleString([], { weekday: "short", hour: "2-digit", minute: "2-digit" }) + ". The bell still counts." : "No popups, sounds or desktop notifications. The bell still counts.";
    var ds = $("[data-ns-desktop-state]", nsDlg);
    if (ds && "Notification" in window && Notification.permission === "denied") ds.textContent = "Blocked in this browser. Allow notifications for this site to turn it on.";
    pushStatus();
  }
  on(document, "click", function (e) {
    if (e.target.closest("[data-notify-settings-open]")) { e.preventDefault(); closeMenus(); nsSync(); openDialog(nsDlg); }
    if (e.target.closest("[data-ns-preview]")) play(ns.tone || N.sound || "chime", ns.volume || 0.6);
    if (e.target.closest("[data-sound-preview]")) {
      var pick = $("#id_sound"), lvl = $("input[name=level]:checked");
      play((pick && pick.value) || LEVEL_SOUND[lvl ? lvl.value : "info"] || N.sound || "chime", ns.volume || 0.6);
    }
    var d = e.target.closest("[data-ns-dnd] [data-value]");
    if (d) {
      var v = d.dataset.value;
      if (v === "0") ns.dnd = 0;
      else if (v === "tomorrow") { var t = new Date(); t.setDate(t.getDate() + 1); t.setHours(8, 0, 0, 0); ns.dnd = t.getTime(); }
      else ns.dnd = Date.now() + (+v) * 60000;
      ns.dndKind = v;
      saveNs();
      nsSync();
    }
    if (e.target.closest("[data-ns-test]") && P.test) post(P.test, new URLSearchParams()).then(function () { toast("Test sent"); });
  });
  on(nsDlg, "change", function (e) {
    var el = e.target.closest("[data-ns]");
    if (!el) return;
    var k = el.dataset.ns;
    ns[k] = el.type === "checkbox" ? el.checked : el.type === "range" ? +el.value : el.value;
    if (k === "desktop" && el.checked && "Notification" in window && Notification.permission !== "granted") {
      Notification.requestPermission().then(function (p) { if (p !== "granted") { ns.desktop = false; saveNs(); nsSync(); toast("The browser did not allow notifications", "error"); } });
    }
    if (k === "volume" || k === "tone") play(ns.tone || N.sound || "chime", ns.volume);
    if (k === "live") startLive();
    saveNs();
    nsSync();
  });

  function b64key(b) {
    var pad = "=".repeat((4 - b.length % 4) % 4);
    var raw = atob((b + pad).replace(/-/g, "+").replace(/_/g, "/"));
    var out = new Uint8Array(raw.length);
    for (var i = 0; i < raw.length; i++) out[i] = raw.charCodeAt(i);
    return out;
  }
  var pushReg = null;
  function pushSupported() { return P.enabled && "serviceWorker" in navigator && "PushManager" in window && window.isSecureContext; }
  function registration() {
    if (pushReg) return Promise.resolve(pushReg);
    return navigator.serviceWorker.register(P.sw, { scope: P.scope }).then(function (r) { pushReg = r; return r; });
  }
  function pushStatus() {
    var toggle = $("[data-ns-push]"), state = $("[data-ns-push-state]");
    if (!toggle) return;
    if (!pushSupported()) { toggle.disabled = true; if (state) state.textContent = window.isSecureContext ? "This browser does not support push." : "Push needs HTTPS."; return; }
    registration().then(function (r) { return r.pushManager.getSubscription(); }).then(function (sub) {
      pushOn = !!sub;
      toggle.checked = pushOn;
      if (state) state.textContent = pushOn ? "On for this device, even when the admin is closed." : "Get notifications even when the admin is closed.";
    }).catch(function () {});
  }
  if (pushSupported()) registration().then(function (r) { return r.pushManager.getSubscription(); }).then(function (sub) { pushOn = !!sub; }).catch(function () {});
  on(document, "change", function (e) {
    if (!e.target.matches("[data-ns-push]")) return;
    var want = e.target.checked;
    registration().then(function (r) {
      if (!want) return r.pushManager.getSubscription().then(function (sub) { if (!sub) return; return post(P.unsubscribe, { endpoint: sub.endpoint }, true).then(function () { return sub.unsubscribe(); }); });
      return Notification.requestPermission().then(function (p) {
        if (p !== "granted") throw new Error("denied");
        return r.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey: b64key(P.key) });
      }).then(function (sub) { return post(P.subscribe, sub.toJSON(), true); });
    }).then(function () { toast(want ? "Push is on for this device" : "Push is off for this device"); pushStatus(); })
      .catch(function () { toast("Could not change push for this device", "error"); pushStatus(); });
  });

  applyPrefs(prefs);
  applyLook();
})();
