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

  on(document, "click", function (e) {
    var btn = e.target.closest("[data-pref] [data-value]");
    if (!btn) return;
    var key = btn.closest("[data-pref]").dataset.pref;
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
    if (e.target.closest("[data-keys-open]")) { e.preventDefault(); openDialog($("[data-keys]")); }
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

  $$(".cc-avatar[data-seed]").forEach(function (a) {
    var s = a.dataset.seed || "", h = 0;
    for (var i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) % 360;
    a.style.setProperty("--h", h);
  });

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
  $$("[data-recent-list]").forEach(function (list) {
    if (!recent.length) { list.innerHTML = '<li class="cc-muted cc-list-empty">' + esc(list.dataset.empty) + "</li>"; return; }
    list.innerHTML = recent.slice(0, 7).map(function (r) {
      return '<li><a class="cc-list-row" href="' + esc(r.url) + '"><span class="cc-list-icon">' + icon("rotate-ccw-clock") + '</span><span class="cc-list-text"><b>' + esc(r.title) + "</b><small>" + esc(r.model) + '</small></span><span class="cc-list-meta">' + ago(r.at) + "</span></a></li>";
    }).join("");
  });
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
      if (config.shortcuts) out.push({ title: "Keyboard shortcuts", icon: "keyboard", kind: "Help", group: "Help", run: function () { openDialog($("[data-keys]")); } });
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
      if (q) {
        items.sort(function (a, b) { return order.indexOf(a.group) - order.indexOf(b.group) || (b._s || 0) - (a._s || 0); });
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

  if (changelist) {
    var key = "cols:" + changelist.dataset.model;
    var hiddenCols = store.get(key, []);
    var menu = $("[data-columns-menu]");
    var holder = $("[data-columns-list]");
    var headers = results ? $$("thead th", results) : [];
    function applyCols() {
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

  $$(".cc-chart-line[data-chart]").forEach(function (chart) {
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
  $$(".cc-chart-bar[data-chart]").forEach(function (chart) {
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
  $$(".cc-donut").forEach(function (d) {
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

  var pending = null, pendingTimer = null;
  on(document, "keydown", function (e) {
    var mod = e.metaKey || e.ctrlKey;
    if (mod && (e.key === "k" || e.key === "K") && config.palette) { e.preventDefault(); palette.open(); return; }
    if (form && mod && (e.key === "s" || e.key === "S")) {
      e.preventDefault();
      var b = $("[data-save-continue]", form) || $("[data-save]", form);
      if (b) b.click();
      return;
    }
    if (form && mod && e.key === "Enter") {
      var s = $("[data-save]", form);
      if (s) { e.preventDefault(); s.click(); }
      return;
    }
    if (e.key === "Escape") {
      if (typing(e) && !anyDialogOpen()) { e.target.blur(); return; }
      closeMenus();
      setSide(false);
      return;
    }
    if (!config.shortcuts || typing(e) || mod || e.altKey || anyDialogOpen()) return;
    var k = e.key;
    if (pending === "g") {
      pending = null; clearTimeout(pendingTimer);
      if (k === "d" || k === "h") { var home = $(".cc-nav-root [data-nav-item]"); if (home) location.href = home.href; }
      if (k === "s") { var site = $(".cc-user .cc-menu a[href]"); if (site) location.href = site.href; }
      return;
    }
    if (k === "g") { pending = "g"; pendingTimer = setTimeout(function () { pending = null; }, 900); return; }
    if (k === "?") { e.preventDefault(); openDialog($("[data-keys]")); return; }
    if (k === "/") {
      var search = $("#searchbar") || $("[data-nav-filter]");
      if (search) { e.preventDefault(); search.focus(); search.select(); }
      return;
    }
    if (k === "t" && config.switcher) { e.preventDefault(); syncPanel(); openDialog($("[data-theme-panel]")); return; }
    if (k === "[") { toggleCollapse(); return; }
    if (changelist) {
      if (k === "j") { e.preventDefault(); setCursor(cursor + 1); return; }
      if (k === "k") { e.preventDefault(); setCursor(cursor - 1); return; }
      if (k === "x" && cursor >= 0) { var cb = $("input.action-select", rows()[cursor]); if (cb) cb.click(); return; }
      if ((k === "o" || k === "Enter") && cursor >= 0) { e.preventDefault(); openRow(e.shiftKey); return; }
      if (k === "n") { var add = $("[data-shortcut-add]"); if (add) location.href = add.href; return; }
      if (k === "f") { var fb = $('[data-drawer-open="filters"]'); if (fb) fb.click(); return; }
      if (k === "ArrowLeft") { var p = $("[data-page-prev]"); if (p) location.href = p.href; return; }
      if (k === "ArrowRight") { var nx = $("[data-page-next]"); if (nx) location.href = nx.href; return; }
    }
  });

  applyPrefs(prefs);
})();
