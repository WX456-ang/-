/* Renders the hero sequence and the work waterfall from window.PORTFOLIO (data.js). */
(function () {
  "use strict";

  var data = window.PORTFOLIO;
  if (!data) {
    return;
  }

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var hero = data.hero || [];
  var items = data.items || [];
  var categories = data.categories || [];

  function pad2(value) {
    return value < 10 ? "0" + value : String(value);
  }

  /* --------------------------------------------------------- hero: cursor trail */

  var heroSection = document.getElementById("top");
  var trail = document.getElementById("heroTrail");
  var trailCursor = 0;
  var trailAlive = [];
  var lastPoint = null;
  var MAX_ALIVE = 6;
  var HOLD_MS = 1000;
  var OUT_MS = 380;

  function spawnTrailImage(x, y, dx, dy) {
    var item = hero[trailCursor % hero.length];
    trailCursor += 1;

    var figure = document.createElement("figure");
    figure.className = "hero__item";
    if (item.width > item.height * 1.12) {
      figure.className += " is-wide";
    }

    // a little scatter keeps consecutive frames from stacking on one line
    var scatter = 26;
    figure.style.left = x + (Math.random() * 2 - 1) * scatter + "px";
    figure.style.top = y + (Math.random() * 2 - 1) * scatter + "px";

    var img = document.createElement("img");
    img.src = item.src;
    img.alt = "";
    img.width = item.width;
    img.height = item.height;
    img.decoding = "async";
    figure.appendChild(img);

    var tilt = Number((Math.random() * 10 - 5).toFixed(2));
    var lead = { x: (dx || 0) * 0.5, y: (dy || 0) * 0.5 };
    figure.style.transform =
      "translate(-50%, -50%) translate(" + lead.x + "px, " + lead.y + "px) rotate(" +
      (tilt + (Math.random() * 4 - 2)).toFixed(2) + "deg) scale(0.88)";
    var settled = "translate(-50%, -50%) rotate(" + tilt + "deg) scale(1)";
    trail.appendChild(figure);
    trailAlive.push(figure);

    // flush the start styles so the entry transition actually runs
    void figure.offsetWidth;
    figure.classList.add("is-in");
    figure.style.transform = settled;

    window.setTimeout(function () {
      figure.classList.add("is-out");
      figure.style.transform =
        "translate(-50%, -50%) translate(0px, " + (Math.random() * 26 - 18).toFixed(1) +
        "px) rotate(" + tilt + "deg) scale(1.05)";
      window.setTimeout(function () {
        figure.remove();
        var position = trailAlive.indexOf(figure);
        if (position > -1) {
          trailAlive.splice(position, 1);
        }
      }, OUT_MS);
    }, HOLD_MS);

    while (trailAlive.length > MAX_ALIVE) {
      var oldest = trailAlive.shift();
      if (oldest && oldest.parentNode) {
        oldest.remove();
      }
    }
  }

  if (heroSection && trail && hero.length && !reduceMotion) {
    var minDistance = function () {
      return Math.max(82, window.innerWidth * 0.065);
    };

    heroSection.addEventListener(
      "pointermove",
      function (event) {
        if (event.pointerType === "touch") {
          return;
        }
        var rect = heroSection.getBoundingClientRect();
        var x = event.clientX - rect.left;
        var y = event.clientY - rect.top;
        var dx = lastPoint ? x - lastPoint.x : 0;
        var dy = lastPoint ? y - lastPoint.y : 0;
        if (lastPoint && Math.hypot(dx, dy) < minDistance()) {
          return;
        }
        lastPoint = { x: x, y: y };
        spawnTrailImage(x, y, dx, dy);
      },
      { passive: true }
    );

    // touch devices: reveal images while dragging a finger across the hero
    heroSection.addEventListener(
      "touchmove",
      function (event) {
        var touch = event.touches[0];
        if (!touch) {
          return;
        }
        var rect = heroSection.getBoundingClientRect();
        var x = touch.clientX - rect.left;
        var y = touch.clientY - rect.top;
        if (lastPoint && Math.hypot(x - lastPoint.x, y - lastPoint.y) < minDistance()) {
          return;
        }
        var dx = lastPoint ? x - lastPoint.x : 0;
        var dy = lastPoint ? y - lastPoint.y : 0;
        lastPoint = { x: x, y: y };
        spawnTrailImage(x, y, dx, dy);
      },
      { passive: true }
    );

    // warm the cache so the first images appear instantly
    hero.forEach(function (item) {
      var preload = new Image();
      preload.src = item.src;
    });
  }

  /* ------------------------------------------------------------- waterfall */

  var grid = document.getElementById("grid");

  function buildTile(item, position) {
    var tile = document.createElement("button");
    tile.type = "button";
    tile.className = "tile";
    tile.dataset.category = item.category;
    tile.dataset.index = String(position);
    tile.setAttribute("aria-label", item.project + "，" + item.category + "，查看大图");

    var img = document.createElement("img");
    img.src = item.src;
    img.width = item.width;
    img.height = item.height;
    img.alt = item.project + " — " + item.subtitle;
    img.loading = "lazy";
    img.decoding = "async";

    var meta = document.createElement("span");
    meta.className = "tile__meta";
    var name = document.createElement("span");
    name.className = "tile__name";
    name.textContent = item.project;
    var category = document.createElement("span");
    category.className = "tile__cat";
    category.textContent = item.category;
    meta.appendChild(name);
    meta.appendChild(category);

    tile.appendChild(img);
    tile.appendChild(meta);
    tile.addEventListener("click", function () {
      openLightbox(position);
    });
    return tile;
  }

  var tiles = [];
  var visible = items.slice();

  function renderGrid(list) {
    if (!grid) {
      return;
    }
    grid.textContent = "";
    tiles = [];
    list.forEach(function (item) {
      var tile = buildTile(item, items.indexOf(item));
      grid.appendChild(tile);
      tiles.push(tile);
    });
    observeTiles();
  }

  var observer = null;

  function observeTiles() {
    if (reduceMotion || !("IntersectionObserver" in window)) {
      tiles.forEach(function (tile) {
        tile.classList.add("is-in");
      });
      return;
    }
    if (!observer) {
      observer = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            if (entry.isIntersecting) {
              entry.target.classList.add("is-in");
              observer.unobserve(entry.target);
            }
          });
        },
        { rootMargin: "0px 0px -8% 0px", threshold: 0.05 }
      );
    }
    tiles.forEach(function (tile) {
      observer.observe(tile);
    });
  }

  /* ---------------------------------------------------------------- filters */

  var filterBar = document.getElementById("filters");

  function setFilter(name) {
    visible = name === "__all__" ? items.slice() : items.filter(function (item) {
      return item.category === name;
    });
    renderGrid(visible);
    Array.prototype.forEach.call(filterBar.querySelectorAll(".filter"), function (button) {
      button.setAttribute("aria-pressed", button.dataset.category === name ? "true" : "false");
    });
  }

  if (filterBar) {
    var allButton = document.createElement("button");
    allButton.type = "button";
    allButton.className = "filter";
    allButton.dataset.category = "__all__";
    allButton.textContent = "全部 " + pad2(items.length);
    allButton.setAttribute("aria-pressed", "true");
    allButton.addEventListener("click", function () {
      setFilter("__all__");
    });
    filterBar.appendChild(allButton);

    categories.forEach(function (name) {
      var count = items.filter(function (item) {
        return item.category === name;
      }).length;
      var button = document.createElement("button");
      button.type = "button";
      button.className = "filter";
      button.dataset.category = name;
      button.textContent = name + " " + pad2(count);
      button.setAttribute("aria-pressed", "false");
      button.addEventListener("click", function () {
        setFilter(name);
      });
      filterBar.appendChild(button);
    });
  }

  renderGrid(visible);

  /* -------------------------------------------------------------- lightbox */

  var lightbox = document.createElement("div");
  lightbox.className = "lightbox";
  lightbox.setAttribute("role", "dialog");
  lightbox.setAttribute("aria-modal", "true");
  lightbox.setAttribute("aria-label", "作品大图");
  lightbox.innerHTML =
    '<div class="lightbox__stage"><img alt=""></div>' +
    '<div class="lightbox__bar">' +
    '<span class="lightbox__info"><span class="lightbox__title"></span>' +
    '<span class="lightbox__sub"></span></span>' +
    '<span class="lightbox__controls">' +
    '<button type="button" data-action="prev">← 上一张</button>' +
    '<button type="button" data-action="next">下一张 →</button>' +
    "</span></div>" +
    '<button type="button" class="lightbox__close" data-action="close">关闭 ✕</button>';
  document.body.appendChild(lightbox);

  var lightboxImage = lightbox.querySelector("img");
  var lightboxTitle = lightbox.querySelector(".lightbox__title");
  var lightboxSub = lightbox.querySelector(".lightbox__sub");
  var lightboxIndex = 0;
  var lastFocus = null;

  function paintLightbox() {
    var item = visible[lightboxIndex];
    if (!item) {
      return;
    }
    lightboxImage.src = item.src;
    lightboxImage.alt = item.project + " — " + item.subtitle;
    lightboxTitle.textContent = item.project + "　" + pad2(lightboxIndex + 1) + " / " + pad2(visible.length);
    lightboxSub.textContent = item.category + " · " + item.subtitle;
  }

  function openLightbox(position) {
    lightboxIndex = Math.max(0, Math.min(visible.length - 1, position));
    paintLightbox();
    lastFocus = document.activeElement;
    lightbox.classList.add("is-open");
    document.body.style.overflow = "hidden";
    lightbox.querySelector('[data-action="close"]').focus();
  }

  function closeLightbox() {
    lightbox.classList.remove("is-open");
    document.body.style.overflow = "";
    if (lastFocus && lastFocus.focus) {
      lastFocus.focus();
    }
  }

  function stepLightbox(delta) {
    if (!visible.length) {
      return;
    }
    lightboxIndex = (lightboxIndex + delta + visible.length) % visible.length;
    paintLightbox();
  }

  lightbox.addEventListener("click", function (event) {
    var action = event.target.getAttribute && event.target.getAttribute("data-action");
    if (action === "prev") {
      stepLightbox(-1);
    } else if (action === "next") {
      stepLightbox(1);
    } else if (action === "close" || event.target === lightbox) {
      closeLightbox();
    }
  });

  document.addEventListener("keydown", function (event) {
    if (!lightbox.classList.contains("is-open")) {
      return;
    }
    if (event.key === "Escape") {
      closeLightbox();
    } else if (event.key === "ArrowLeft") {
      stepLightbox(-1);
    } else if (event.key === "ArrowRight") {
      stepLightbox(1);
    }
  });

  /* ----------------------------------------------------------- topbar state */

  var topbar = document.getElementById("topbar");
  if (topbar) {
    var onScroll = function () {
      topbar.classList.toggle("is-scrolled", window.scrollY > 40);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }
})();
