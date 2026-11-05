/* ==========================================================================
   Maison Aurévia — logique propre à chaque page
   (accueil, boutique, fiche produit, panier, confirmation)
   ========================================================================== */

(function () {
  "use strict";

  var MA = window.MA;
  var page = document.body.getAttribute("data-page");

  function erreurCatalogue(conteneur) {
    conteneur.innerHTML =
      '<div class="vide"><h3>Le catalogue n’a pas pu être chargé</h3>' +
      "<p>Ouvrez le site via un serveur local (voir le README) ou réessayez dans un instant.</p></div>";
  }

  /* ---------------------------------------------------------------- Accueil */

  function accueil() {
    var grille = document.getElementById("selection");
    if (!grille) return;
    MA.chargerProduits()
      .then(function (produits) {
        var choix = produits
          .filter(function (p) { return p.stock > 0; })
          .sort(function (a, b) { return (b.nouveau - a.nouveau) || b.date.localeCompare(a.date); })
          .slice(0, 4);
        grille.innerHTML = choix.map(MA.carteProduit).join("");
        MA.observer(grille.querySelectorAll(".reveal"));
      })
      .catch(function () { erreurCatalogue(grille); });
  }

  /* --------------------------------------------------------------- Boutique */

  function boutique() {
    var grille = document.getElementById("catalogue");
    var selMarque = document.getElementById("filtre-marque");
    var selType = document.getElementById("filtre-type");
    var selTri = document.getElementById("filtre-tri");
    var compte = document.getElementById("compte-resultats");
    var reset = document.getElementById("filtres-reset");
    if (!grille) return;

    var produits = [];

    function remplir(select, valeurs, libelleTous) {
      select.innerHTML =
        '<option value="">' + libelleTous + "</option>" +
        valeurs.map(function (v) {
          return '<option value="' + MA.echapper(v.valeur) + '">' + MA.echapper(v.libelle) + "</option>";
        }).join("");
    }

    function lireUrl() {
      var params = new URLSearchParams(location.search);
      return {
        marque: params.get("marque") || "",
        type: params.get("type") || "",
        tri: params.get("tri") || "nouveautes",
      };
    }

    function ecrireUrl(etat) {
      var params = new URLSearchParams();
      if (etat.marque) params.set("marque", etat.marque);
      if (etat.type) params.set("type", etat.type);
      if (etat.tri && etat.tri !== "nouveautes") params.set("tri", etat.tri);
      var qs = params.toString();
      history.replaceState(null, "", location.pathname + (qs ? "?" + qs : ""));
    }

    // Le filtre « Produit » accepte un type (Casquette, Bob, Sneakers) ou un modèle (B22, B30)
    function correspondType(p, valeur) {
      if (!valeur) return true;
      return p.type === valeur || p.modele === valeur;
    }

    function afficher() {
      var etat = { marque: selMarque.value, type: selType.value, tri: selTri.value };
      ecrireUrl(etat);

      var liste = produits.filter(function (p) {
        return (!etat.marque || p.marque === etat.marque) && correspondType(p, etat.type);
      });

      liste.sort(function (a, b) {
        if (etat.tri === "prix-asc") return a.prix - b.prix;
        if (etat.tri === "prix-desc") return b.prix - a.prix;
        return (b.stock > 0) - (a.stock > 0) || b.date.localeCompare(a.date);
      });

      compte.textContent = liste.length + (liste.length > 1 ? " pièces" : " pièce");
      reset.hidden = !(etat.marque || etat.type || etat.tri !== "nouveautes");

      if (!liste.length) {
        grille.innerHTML =
          '<div class="vide"><h3>Aucune pièce ne correspond</h3>' +
          "<p>Cette combinaison n’est pas disponible pour le moment. Nos arrivages sont fréquents.</p>" +
          '<button class="btn magnetique" type="button" data-reset><span class="btn__texte">Voir toutes les pièces</span></button></div>';
        MA.magnetique(grille);
        return;
      }
      grille.innerHTML = liste.map(MA.carteProduit).join("");
      MA.observer(grille.querySelectorAll(".reveal"));
    }

    function reinitialiser() {
      selMarque.value = "";
      selType.value = "";
      selTri.value = "nouveautes";
      afficher();
    }

    MA.chargerProduits()
      .then(function (data) {
        produits = data;
        var marques = Array.from(new Set(data.map(function (p) { return p.marque; }))).sort();
        remplir(selMarque, marques.map(function (m) { return { valeur: m, libelle: m }; }), "Toutes les maisons");

        var types = [
          { valeur: "Casquette", libelle: "Casquettes" },
          { valeur: "Bob", libelle: "Bobs" },
          { valeur: "Sneakers", libelle: "Sneakers (toutes)" },
        ];
        Array.from(new Set(data.map(function (p) { return p.modele; }).filter(Boolean)))
          .sort()
          .forEach(function (m) { types.push({ valeur: m, libelle: "Dior " + m }); });
        remplir(selType, types, "Tous les produits");

        var etat = lireUrl();
        selMarque.value = etat.marque;
        selType.value = etat.type;
        selTri.value = etat.tri;
        // valeurs inconnues dans l'URL → retour à « tous »
        if (selMarque.value !== etat.marque) selMarque.value = "";
        if (selType.value !== etat.type) selType.value = "";
        if (!selTri.value) selTri.value = "nouveautes";

        [selMarque, selType, selTri].forEach(function (s) { s.addEventListener("change", afficher); });
        reset.addEventListener("click", reinitialiser);
        grille.addEventListener("click", function (e) {
          if (e.target.closest("[data-reset]")) reinitialiser();
        });
        afficher();
      })
      .catch(function () { erreurCatalogue(grille); });
  }

  /* ----------------------------------------------------------- Fiche produit */

  function produit() {
    var zone = document.getElementById("fiche");
    if (!zone) return;
    var id = new URLSearchParams(location.search).get("id");

    MA.chargerProduits()
      .then(function (produits) {
        var p = produits.find(function (x) { return x.id === id; });
        if (!p) {
          zone.innerHTML =
            '<div class="vide"><h2>Pièce introuvable</h2><p>Elle a peut-être déjà trouvé preneur.</p>' +
            '<a class="btn magnetique" href="/boutique.html"><span class="btn__texte">Retour à la boutique</span></a></div>';
          MA.magnetique(zone);
          return;
        }
        document.title = p.marque + " " + p.nom + " — Maison Aurévia";
        var meta = document.querySelector('meta[name="description"]');
        if (meta) meta.setAttribute("content", p.marque + " " + p.nom + ", " + p.couleur + ". " + p.description);

        var dispo = p.stock > 0;
        var e = MA.echapper;
        zone.innerHTML =
          '<div class="fiche">' +
          '<div class="fiche__visuel reveal reveal--gauche">' +
          '<div class="badges">' + (p.nouveau ? '<span class="badge badge--plein">Nouveauté</span>' : "") +
          '<span class="badge">' + (dispo ? "Authentifié" : "Vendu") + "</span></div>" +
          MA.visuel(p) +
          "</div>" +
          '<div class="reveal reveal--droite">' +
          '<p class="fiche__fil"><a href="/boutique.html">Boutique</a> / <a href="/boutique.html?marque=' + encodeURIComponent(p.marque) + '">' + e(p.marque) + "</a></p>" +
          '<span class="surtitre surtitre--gauche">' + e(p.marque) + "</span>" +
          "<h1>" + e(p.nom) + "</h1>" +
          '<span class="prix">' + MA.prix(p.prix) + "</span>" +
          "<p>" + e(p.description) + "</p>" +
          '<ul class="caracteristiques">' +
          "<li><span>Maison</span><span>" + e(p.marque) + "</span></li>" +
          "<li><span>Produit</span><span>" + e(p.type + (p.modele ? " " + p.modele : "")) + "</span></li>" +
          "<li><span>Coloris</span><span>" + e(p.couleur) + "</span></li>" +
          "<li><span>Taille</span><span>" + e(p.taille) + "</span></li>" +
          "<li><span>État</span><span>" + e(p.etat) + "</span></li>" +
          "</ul>" +
          '<button class="btn btn--plein btn--bloc magnetique" data-force="0.18" type="button" data-ajouter="' + e(p.id) + '"' + (dispo ? "" : " disabled") + ">" +
          '<span class="btn__texte">' + (dispo ? "Ajouter au panier" : "Pièce vendue") + "</span></button>" +
          '<div class="garanties">' +
          "<div>" + MA.icones.bouclier + "<span>Authenticité vérifiée par nos experts</span></div>" +
          "<div>" + MA.icones.camion + "<span>Expédition soignée et suivie sous 48 h ouvrées</span></div>" +
          "<div>" + MA.icones.retour + "<span>14 jours pour changer d’avis</span></div>" +
          "<div>" + MA.icones.cadenas + "<span>Paiement 100 % sécurisé par Stripe</span></div>" +
          "</div></div></div>";
        MA.observer(zone.querySelectorAll(".reveal"));
        MA.magnetique(zone);
      })
      .catch(function () { erreurCatalogue(zone); });
  }

  /* ------------------------------------------------------------------ Panier */

  function panier() {
    var zone = document.getElementById("panier");
    if (!zone) return;
    var produits = [];

    function rendre() {
      var lignes = MA.panier.lignes()
        .map(function (l) {
          var p = produits.find(function (x) { return x.id === l.id; });
          return p ? { p: p, qte: Math.min(l.qte, p.stock) } : null;
        })
        .filter(function (l) { return l && l.qte > 0; });

      if (!lignes.length) {
        zone.innerHTML =
          '<div class="vide reveal"><h2>Votre panier est vide</h2>' +
          "<p>Découvrez notre sélection de pièces authentifiées.</p>" +
          '<a class="btn btn--plein magnetique" href="/boutique.html"><span class="btn__texte">Découvrir la boutique</span></a></div>';
        MA.observer(zone.querySelectorAll(".reveal"));
        MA.magnetique(zone);
        return;
      }

      var total = lignes.reduce(function (s, l) { return s + l.p.prix * l.qte; }, 0);
      var e = MA.echapper;

      zone.innerHTML =
        '<div class="panier">' +
        '<div class="panier__liste">' +
        lignes.map(function (l) {
          var lien = "/produit.html?id=" + encodeURIComponent(l.p.id);
          return (
            '<div class="ligne-panier">' +
            '<a class="ligne-panier__visuel" href="' + lien + '">' + MA.visuel(l.p) + "</a>" +
            "<div>" +
            '<span class="produit__marque">' + e(l.p.marque) + "</span>" +
            '<h3><a href="' + lien + '">' + e(l.p.nom) + "</a></h3>" +
            '<p class="produit__detail">' + e(l.p.couleur) + " · " + e(l.p.taille) + (l.qte > 1 ? " · Qté " + l.qte : "") + "</p>" +
            "</div>" +
            '<div class="ligne-panier__droite">' +
            '<span class="prix">' + MA.prix(l.p.prix * l.qte) + "</span>" +
            '<button class="lien-retirer" type="button" data-retirer="' + e(l.p.id) + '">Retirer</button>' +
            "</div></div>"
          );
        }).join("") +
        "</div>" +
        '<aside class="recap" aria-labelledby="titre-recap">' +
        '<h2 id="titre-recap">Récapitulatif</h2>' +
        '<div class="recap__ligne"><span>Sous-total</span><span>' + MA.prix(total) + "</span></div>" +
        '<div class="recap__ligne"><span>Livraison (France)</span><span>Offerte</span></div>' +
        '<div class="recap__total"><span>Total TTC</span><strong>' + MA.prix(total) + "</strong></div>" +
        '<label class="case"><input type="checkbox" id="accepte-cgv"> <span>J’ai lu et j’accepte les <a href="/cgv.html" target="_blank" rel="noopener">conditions générales de vente</a> et la <a href="/confidentialite.html" target="_blank" rel="noopener">politique de confidentialité</a>.</span></label>' +
        '<button class="btn btn--plein btn--bloc magnetique" data-force="0.18" id="payer" type="button" style="margin-top:22px"><span class="btn__texte">Paiement sécurisé</span></button>' +
        '<div class="message-erreur" id="erreur-paiement" role="alert"></div>' +
        '<p class="recap__note">Vous serez redirigé vers Stripe pour régler en toute sécurité.</p>' +
        '<div class="paiements"><span>Visa</span><span>Mastercard</span><span>CB</span><span>Apple Pay</span><span>Google Pay</span></div>' +
        "</aside></div>";

      MA.magnetique(zone);
      document.getElementById("payer").addEventListener("click", function () { payer(lignes, this); });
    }

    function payer(lignes, bouton) {
      var erreur = document.getElementById("erreur-paiement");
      erreur.classList.remove("est-visible");
      if (!document.getElementById("accepte-cgv").checked) {
        erreur.textContent = "Merci d’accepter les conditions générales de vente pour continuer.";
        erreur.classList.add("est-visible");
        return;
      }
      bouton.disabled = true;
      bouton.querySelector(".btn__texte").textContent = "Redirection…";

      fetch("/.netlify/functions/creer-paiement", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          articles: lignes.map(function (l) { return { id: l.p.id, qte: l.qte }; }),
        }),
      })
        .then(function (r) {
          return r.json().catch(function () { return {}; }).then(function (data) {
            if (!r.ok || !data.url) throw new Error(data.erreur || "Le paiement est momentanément indisponible.");
            return data;
          });
        })
        .then(function (data) {
          location.href = data.url;
        })
        .catch(function (err) {
          erreur.textContent = err.message === "Failed to fetch"
            ? "Le service de paiement est injoignable. Vérifiez votre connexion."
            : err.message;
          erreur.classList.add("est-visible");
          bouton.disabled = false;
          bouton.querySelector(".btn__texte").textContent = "Paiement sécurisé";
        });
    }

    zone.addEventListener("click", function (e) {
      var b = e.target.closest("[data-retirer]");
      if (b) MA.panier.retirer(b.getAttribute("data-retirer"));
    });
    document.addEventListener("panier:maj", rendre);

    MA.chargerProduits()
      .then(function (data) {
        produits = data;
        rendre();
      })
      .catch(function () { erreurCatalogue(zone); });
  }

  /* --------------------------------------------------------- Confirmation */

  function succes() {
    MA.panier.vider();
  }

  var routes = { accueil: accueil, boutique: boutique, produit: produit, panier: panier, succes: succes };
  if (routes[page]) {
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", routes[page]);
    else routes[page]();
  }
})();
