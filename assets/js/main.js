/* ==========================================================================
   Maison Aurévia — script commun
   Mise en page (header/footer), panier, animations.
   Toutes les animations n'utilisent que transform/opacity (60 fps)
   et sont coupées si prefers-reduced-motion est activé.
   ========================================================================== */

(function () {
  "use strict";

  document.documentElement.classList.add("js");

  var mqReduit = window.matchMedia("(prefers-reduced-motion: reduce)");
  var mqSouris = window.matchMedia("(hover: hover) and (pointer: fine)");
  var CLE_PANIER = "maison-aurevia-panier";

  /* ----------------------------------------------------------------------
     Utilitaires
     ---------------------------------------------------------------------- */

  var formatPrix = new Intl.NumberFormat("fr-FR", {
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 0,
  });

  function prix(valeur) {
    return formatPrix.format(valeur);
  }

  function echapper(texte) {
    return String(texte == null ? "" : texte)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  var cacheProduits = null;
  function chargerProduits() {
    if (!cacheProduits) {
      cacheProduits = fetch("/data/products.json", { cache: "no-cache" })
        .then(function (r) {
          if (!r.ok) throw new Error("Catalogue indisponible");
          return r.json();
        })
        .catch(function (e) {
          cacheProduits = null;
          throw e;
        });
    }
    return cacheProduits;
  }

  /* ----------------------------------------------------------------------
     Icônes & visuels de remplacement (en attendant les vraies photos)
     ---------------------------------------------------------------------- */

  var ICONES = {
    panier:
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" aria-hidden="true"><path d="M5 8h14l-1.2 12H6.2L5 8Z"/><path d="M9 8V6.5a3 3 0 0 1 6 0V8"/></svg>',
    plus:
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg>',
    check:
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" aria-hidden="true"><path d="m5 12.5 4.5 4.5L19 7.5"/></svg>',
    bouclier:
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.1" aria-hidden="true"><path d="M12 3 4.5 6v5.5c0 4.6 3.2 8.4 7.5 9.5 4.3-1.1 7.5-4.9 7.5-9.5V6L12 3Z"/><path d="m8.8 12 2.2 2.2 4.2-4.4"/></svg>',
    camion:
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.1" aria-hidden="true"><path d="M2.5 6.5h11v9h-11zM13.5 9.5h4l3 3v3h-7"/><circle cx="6.5" cy="17.5" r="1.7"/><circle cx="17" cy="17.5" r="1.7"/></svg>',
    retour:
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.1" aria-hidden="true"><path d="M4 9h11a5 5 0 0 1 0 10H8"/><path d="m8 5-4 4 4 4"/></svg>',
    cadenas:
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.1" aria-hidden="true"><rect x="5" y="10.5" width="14" height="10" rx="1"/><path d="M8 10.5V7.5a4 4 0 0 1 8 0v3"/></svg>',
  };

  var SILHOUETTES = {
    Casquette:
      '<svg viewBox="0 0 140 90" fill="none" stroke="currentColor" stroke-width="1.2" aria-hidden="true"><path d="M26 58C24 30 46 14 70 14s44 14 44 40"/><path d="M70 14c-6 12-8 26-8 42M70 14c9 10 15 24 17 40"/><path d="M26 58c26-8 62-8 88-4 10 2 18 8 20 16-24-6-60-8-88-4-12 2-20-2-20-8Z"/><circle cx="70" cy="13" r="2.6"/></svg>',
    Bob:
      '<svg viewBox="0 0 140 90" fill="none" stroke="currentColor" stroke-width="1.2" aria-hidden="true"><path d="M40 52 46 22c1-6 47-6 48 0l6 30"/><path d="M42 44c18 4 38 4 56 0" stroke-dasharray="3 3"/><path d="M12 62c10-12 106-12 116 0-8 9-108 9-116 0Z"/><path d="M40 52c20 4 40 4 60 0"/></svg>',
    Sneakers:
      '<svg viewBox="0 0 140 90" fill="none" stroke="currentColor" stroke-width="1.2" aria-hidden="true"><path d="M12 64V48c16 0 30-6 40-22l16 4c6 12 22 18 44 20 12 1 18 6 18 14v4H12Z"/><path d="M12 68h118M12 74h118" /><path d="m56 32 6 8M62 30l6 8M68 32l5 7"/><path d="M84 48c6 4 14 6 26 6"/></svg>',
  };

  function visuel(p, classeImg) {
    var src = p.image || "/images/produits/" + p.id + ".jpg";
    var nomComplet = p.marque + " — " + p.nom;
    return (
      '<div class="placeholder">' +
      (SILHOUETTES[p.type] || SILHOUETTES.Casquette) +
      "<span>Photo à venir</span></div>" +
      '<img src="' + echapper(src) + '" alt="' + echapper(nomComplet + ", " + p.couleur) + '"' +
      ' loading="lazy" decoding="async"' + (classeImg ? ' class="' + classeImg + '"' : "") +
      " onerror=\"this.remove()\" onload=\"this.previousElementSibling&&this.previousElementSibling.remove()\">"
    );
  }

  function carteProduit(p) {
    var lien = "/produit.html?id=" + encodeURIComponent(p.id);
    var dispo = p.stock > 0;
    var badges = "";
    if (p.nouveau) badges += '<span class="badge badge--plein">Nouveauté</span>';
    if (!dispo) badges += '<span class="badge">Vendu</span>';
    else badges += '<span class="badge">Authentifié</span>';

    return (
      '<article class="produit reveal">' +
      '<a class="produit__visuel" href="' + lien + '" tabindex="-1" aria-hidden="true">' +
      '<div class="badges">' + badges + "</div>" +
      visuel(p) +
      "</a>" +
      '<div class="produit__infos">' +
      '<span class="produit__marque">' + echapper(p.marque) + "</span>" +
      '<h3 class="produit__nom"><a href="' + lien + '">' + echapper(p.nom) + "</a></h3>" +
      '<p class="produit__detail">' + echapper(p.couleur) + " · " + echapper(p.taille) + "</p>" +
      '<div class="produit__pied">' +
      '<span class="prix">' + prix(p.prix) + "</span>" +
      '<button class="produit__ajout" type="button" data-ajouter="' + echapper(p.id) + '"' +
      (dispo ? "" : " disabled") +
      ' aria-label="Ajouter ' + echapper(p.marque + " " + p.nom) + ' au panier">' +
      ICONES.plus +
      "</button>" +
      "</div></div></article>"
    );
  }

  /* ----------------------------------------------------------------------
     Header & pied de page communs
     ---------------------------------------------------------------------- */

  var PAGES = [
    { href: "/", libelle: "Accueil", cle: "accueil" },
    { href: "/boutique.html", libelle: "Boutique", cle: "boutique" },
    { href: "/#rachat", libelle: "Vendre une pièce", cle: "rachat" },
    { href: "/#contact", libelle: "Contact", cle: "contact" },
  ];

  function construireHeader() {
    var cible = document.getElementById("header");
    if (!cible) return;
    var page = document.body.getAttribute("data-page");
    var liens = PAGES.map(function (l) {
      return (
        '<li><a href="' + l.href + '"' + (l.cle === page ? ' aria-current="page"' : "") + ">" +
        l.libelle + "</a></li>"
      );
    }).join("");

    cible.outerHTML =
      '<a class="lien-evitement" href="#contenu">Aller au contenu</a>' +
      '<header class="header" id="header">' +
      '<div class="conteneur header__inner">' +
      '<a class="marque" href="/" aria-label="Maison Aurévia — accueil">' +
      '<img src="/assets/img/monogramme.png" alt="" width="46" height="46">' +
      '<span class="marque__nom">Maison Aurévia<span class="marque__sous">Paris · Luxe de seconde main</span></span>' +
      "</a>" +
      '<nav class="nav" aria-label="Navigation principale">' +
      '<ul class="nav__liens" id="menu">' + liens + "</ul>" +
      '<a class="panier-btn" href="/panier.html" aria-label="Panier">' + ICONES.panier +
      '<span class="panier-btn__compte" data-compte-panier aria-live="polite">0</span></a>' +
      '<button class="burger" type="button" aria-controls="menu" aria-expanded="false" aria-label="Ouvrir le menu"><span></span><span></span><span></span></button>' +
      "</nav></div></header>";
  }

  function construirePied() {
    var cible = document.getElementById("pied");
    if (!cible) return;
    var annee = new Date().getFullYear();
    cible.outerHTML =
      '<footer class="pied">' +
      '<div class="conteneur">' +
      '<div class="pied__grille">' +
      "<div>" +
      '<img class="pied__logo" src="/assets/img/logo-maison-aurevia.png" alt="Maison Aurévia — Achat &amp; revente d’articles de luxe, Paris" width="210" height="149" loading="lazy">' +
      "<p>Pièces de luxe authentifiées, sélectionnées une à une à Paris.</p>" +
      "</div>" +
      "<div><h4>Boutique</h4><ul>" +
      '<li><a href="/boutique.html?type=Casquette">Casquettes</a></li>' +
      '<li><a href="/boutique.html?type=Bob">Bobs</a></li>' +
      '<li><a href="/boutique.html?type=Sneakers">Sneakers Dior B22 / B30</a></li>' +
      '<li><a href="/#rachat">Vendre une pièce</a></li>' +
      "</ul></div>" +
      "<div><h4>Informations</h4><ul>" +
      '<li><a href="/livraison.html">Livraison</a></li>' +
      '<li><a href="/retours.html">Retours &amp; rétractation</a></li>' +
      '<li><a href="/#contact">Contact</a></li>' +
      "</ul></div>" +
      "<div><h4>Légal</h4><ul>" +
      '<li><a href="/cgv.html">Conditions générales de vente</a></li>' +
      '<li><a href="/mentions-legales.html">Mentions légales</a></li>' +
      '<li><a href="/confidentialite.html">Confidentialité &amp; cookies</a></li>' +
      "</ul></div>" +
      "</div>" +
      '<div class="pied__bas">' +
      "<span>© " + annee + " Maison Aurévia — Paris</span>" +
      '<span class="pied__mention">Maison Aurévia est un revendeur indépendant d’articles d’occasion. Les marques citées appartiennent à leurs propriétaires respectifs ; Maison Aurévia n’est affiliée à aucune d’entre elles.</span>' +
      "</div></div></footer>" +
      '<div class="toast" role="status" aria-live="polite" id="toast"></div>';
  }

  function initMenu() {
    var burger = document.querySelector(".burger");
    if (!burger) return;
    function fermer() {
      document.body.classList.remove("menu-ouvert");
      burger.setAttribute("aria-expanded", "false");
      burger.setAttribute("aria-label", "Ouvrir le menu");
    }
    burger.addEventListener("click", function () {
      var ouvert = document.body.classList.toggle("menu-ouvert");
      burger.setAttribute("aria-expanded", String(ouvert));
      burger.setAttribute("aria-label", ouvert ? "Fermer le menu" : "Ouvrir le menu");
    });
    document.querySelectorAll(".nav__liens a").forEach(function (a) {
      a.addEventListener("click", fermer);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") fermer();
    });
  }

  /* ----------------------------------------------------------------------
     Panier (localStorage — protégé par try/catch)
     ---------------------------------------------------------------------- */

  var Panier = {
    lire: function () {
      try {
        var brut = JSON.parse(localStorage.getItem(CLE_PANIER) || "[]");
        return Array.isArray(brut) ? brut.filter(function (l) { return l && l.id && l.qte > 0; }) : [];
      } catch (e) {
        return [];
      }
    },
    ecrire: function (lignes) {
      try {
        localStorage.setItem(CLE_PANIER, JSON.stringify(lignes));
      } catch (e) { /* navigation privée : le panier reste en mémoire de page */ }
      Panier._memoire = lignes;
      majCompteur(true);
      document.dispatchEvent(new CustomEvent("panier:maj"));
    },
    lignes: function () {
      var l = Panier.lire();
      return l.length || !Panier._memoire ? l : Panier._memoire;
    },
    ajouter: function (produit) {
      var lignes = Panier.lignes();
      var ligne = lignes.find(function (l) { return l.id === produit.id; });
      if (ligne) {
        if (ligne.qte >= produit.stock) return false;
        ligne.qte += 1;
      } else {
        lignes.push({ id: produit.id, qte: 1 });
      }
      Panier.ecrire(lignes);
      return true;
    },
    retirer: function (id) {
      Panier.ecrire(Panier.lignes().filter(function (l) { return l.id !== id; }));
    },
    vider: function () {
      Panier.ecrire([]);
    },
    nombre: function () {
      return Panier.lignes().reduce(function (s, l) { return s + l.qte; }, 0);
    },
  };

  function majCompteur(animer) {
    var el = document.querySelector("[data-compte-panier]");
    if (!el) return;
    var n = Panier.nombre();
    el.textContent = n;
    el.classList.toggle("est-visible", n > 0);
    if (animer && n > 0 && !mqReduit.matches) {
      el.classList.remove("pulse");
      void el.offsetWidth;
      el.classList.add("pulse");
    }
  }

  var minuterieToast;
  function toast(html) {
    var t = document.getElementById("toast");
    if (!t) return;
    t.innerHTML = html;
    t.classList.add("est-visible");
    clearTimeout(minuterieToast);
    minuterieToast = setTimeout(function () { t.classList.remove("est-visible"); }, 3800);
  }

  // Délégation : tout bouton [data-ajouter] ajoute au panier
  document.addEventListener("click", function (e) {
    var bouton = e.target.closest("[data-ajouter]");
    if (!bouton) return;
    e.preventDefault();
    var id = bouton.getAttribute("data-ajouter");
    chargerProduits().then(function (produits) {
      var p = produits.find(function (x) { return x.id === id; });
      if (!p) return;
      var ok = Panier.ajouter(p);
      toast(
        ok
          ? ICONES.check.replace("<svg", '<svg width="18" height="18" style="color:var(--or)"') +
            "<span>" + echapper(p.marque + " " + p.nom) + " ajouté au panier</span>" +
            '<a href="/panier.html">Voir le panier</a>'
          : "<span>Pièce unique : elle est déjà dans votre panier.</span>" +
            '<a href="/panier.html">Voir le panier</a>'
      );
    });
  });

  /* ----------------------------------------------------------------------
     Animation 1 — Header qui se compacte au scroll
     ---------------------------------------------------------------------- */

  function initHeader() {
    var header = document.querySelector(".header");
    if (!header) return;
    var compact = false;
    var enAttente = false;
    function maj() {
      enAttente = false;
      var doit = window.scrollY > 60;
      if (doit !== compact) {
        compact = doit;
        header.classList.toggle("est-compact", compact);
      }
    }
    window.addEventListener(
      "scroll",
      function () {
        if (!enAttente) {
          enAttente = true;
          requestAnimationFrame(maj);
        }
      },
      { passive: true }
    );
    maj();
  }

  /* ----------------------------------------------------------------------
     Animation 2 — Apparition au scroll (fade + translation)
     ---------------------------------------------------------------------- */

  var observateurReveal = null;

  function preparerDecalages(racine) {
    (racine || document).querySelectorAll("[data-stagger]").forEach(function (parent) {
      var pas = parseInt(parent.getAttribute("data-stagger"), 10) || 90;
      Array.prototype.forEach.call(parent.children, function (enfant, i) {
        if (enfant.classList.contains("reveal")) {
          enfant.style.setProperty("--delai", Math.min(i * pas, 600) + "ms");
        }
      });
    });
  }

  function observer(elements) {
    elements = elements || document.querySelectorAll(".reveal:not(.est-visible)");
    preparerDecalages();
    if (mqReduit.matches || !("IntersectionObserver" in window)) {
      Array.prototype.forEach.call(elements, function (el) { el.classList.add("est-visible"); });
      return;
    }
    if (!observateurReveal) {
      observateurReveal = new IntersectionObserver(
        function (entrees) {
          entrees.forEach(function (entree) {
            if (entree.isIntersecting) {
              entree.target.classList.add("est-visible");
              observateurReveal.unobserve(entree.target);
            }
          });
        },
        { rootMargin: "0px 0px -8% 0px", threshold: 0.08 }
      );
    }
    Array.prototype.forEach.call(elements, function (el) { observateurReveal.observe(el); });
  }

  /* ----------------------------------------------------------------------
     Animation 3 — Effet magnétique au survol des boutons
     ---------------------------------------------------------------------- */

  function initMagnetique(racine) {
    if (mqReduit.matches || !mqSouris.matches) return;
    (racine || document).querySelectorAll(".magnetique:not([data-mag])").forEach(function (el) {
      el.setAttribute("data-mag", "");
      var texte = el.querySelector(".btn__texte");
      var force = parseFloat(el.getAttribute("data-force")) || 0.32;
      var cible = { x: 0, y: 0 };
      var actuel = { x: 0, y: 0 };
      var rafId = null;
      var rect = null;

      function boucle() {
        actuel.x += (cible.x - actuel.x) * 0.18;
        actuel.y += (cible.y - actuel.y) * 0.18;
        el.style.transform = "translate3d(" + actuel.x.toFixed(2) + "px," + actuel.y.toFixed(2) + "px,0)";
        if (texte) {
          texte.style.transform = "translate3d(" + (actuel.x * 0.35).toFixed(2) + "px," + (actuel.y * 0.35).toFixed(2) + "px,0)";
        }
        if (Math.abs(cible.x - actuel.x) > 0.05 || Math.abs(cible.y - actuel.y) > 0.05) {
          rafId = requestAnimationFrame(boucle);
        } else {
          rafId = null;
        }
      }
      function lancer() {
        if (!rafId) rafId = requestAnimationFrame(boucle);
      }

      el.addEventListener("pointerenter", function () {
        rect = el.getBoundingClientRect();
      });
      el.addEventListener("pointermove", function (e) {
        if (!rect) rect = el.getBoundingClientRect();
        var dx = e.clientX - (rect.left + rect.width / 2);
        var dy = e.clientY - (rect.top + rect.height / 2);
        cible.x = Math.max(-18, Math.min(18, dx * force));
        cible.y = Math.max(-12, Math.min(12, dy * force * 1.2));
        lancer();
      });
      el.addEventListener("pointerleave", function () {
        rect = null;
        cible.x = 0;
        cible.y = 0;
        lancer();
      });
    });
  }

  /* ----------------------------------------------------------------------
     Animation 4 — Chiffres qui défilent à l'apparition
     ---------------------------------------------------------------------- */

  function initCompteurs() {
    var compteurs = document.querySelectorAll("[data-compteur]");
    if (!compteurs.length) return;

    function afficher(el, valeur) {
      el.textContent = (el.getAttribute("data-prefixe") || "") + Math.round(valeur).toLocaleString("fr-FR") + (el.getAttribute("data-suffixe") || "");
    }
    function animer(el) {
      var fin = parseFloat(el.getAttribute("data-compteur"));
      var duree = parseInt(el.getAttribute("data-duree"), 10) || 2000;
      var debut = null;
      function easeOutExpo(t) { return t === 1 ? 1 : 1 - Math.pow(2, -10 * t); }
      function etape(ts) {
        if (debut === null) debut = ts;
        var t = Math.min((ts - debut) / duree, 1);
        afficher(el, fin * easeOutExpo(t));
        if (t < 1) requestAnimationFrame(etape);
      }
      requestAnimationFrame(etape);
    }

    if (mqReduit.matches || !("IntersectionObserver" in window)) {
      compteurs.forEach(function (el) { afficher(el, parseFloat(el.getAttribute("data-compteur"))); });
      return;
    }
    compteurs.forEach(function (el) { afficher(el, 0); });
    var io = new IntersectionObserver(
      function (entrees) {
        entrees.forEach(function (entree) {
          if (entree.isIntersecting) {
            animer(entree.target);
            io.unobserve(entree.target);
          }
        });
      },
      { threshold: 0.6 }
    );
    compteurs.forEach(function (el) { io.observe(el); });
  }

  /* ----------------------------------------------------------------------
     Formulaires Netlify (envoi sans rechargement)
     ---------------------------------------------------------------------- */

  function initFormulaires() {
    document.querySelectorAll("form[data-netlify]").forEach(function (form) {
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        var bouton = form.querySelector('[type="submit"]');
        var donnees = new URLSearchParams(new FormData(form)).toString();
        if (bouton) bouton.disabled = true;
        fetch("/", {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: donnees,
        })
          .then(function (r) {
            if (!r.ok) throw new Error();
            form.reset();
            toast("<span>Merci ! Votre message a bien été envoyé. Nous vous répondons sous 24 h.</span>");
          })
          .catch(function () {
            toast("<span>L’envoi a échoué. Écrivez-nous directement par e-mail.</span>");
          })
          .finally(function () {
            if (bouton) bouton.disabled = false;
          });
      });
    });
  }

  /* ----------------------------------------------------------------------
     Démarrage
     ---------------------------------------------------------------------- */

  construireHeader();
  construirePied();
  initMenu();
  initHeader();
  majCompteur(false);
  window.addEventListener("storage", function () { majCompteur(false); });

  document.addEventListener("DOMContentLoaded", function () {
    observer();
    initMagnetique();
    initCompteurs();
    initFormulaires();
  });

  // API partagée avec les scripts de page
  window.MA = {
    prix: prix,
    echapper: echapper,
    chargerProduits: chargerProduits,
    carteProduit: carteProduit,
    visuel: visuel,
    icones: ICONES,
    panier: Panier,
    toast: toast,
    observer: observer,
    magnetique: initMagnetique,
    mouvementReduit: function () { return mqReduit.matches; },
  };
})();
