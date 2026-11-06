# Maison Aurévia — Achat & revente d’articles de luxe, Paris

Site e-commerce de la direction artistique « Maison noire » (noir, blanc cassé, or champagne).
Il est statique (HTML, CSS, JavaScript) et le paiement passe par **Stripe Checkout** via une
fonction Netlify. Aucun framework n’est utilisé, donc il n’y a rien à compiler.

## Structure

```
index.html              Accueil : hero, compteurs, maisons, sélection, rachat, contact
boutique.html           Catalogue avec 3 filtres (Maison · Produit · Tri)
produit.html?id=…       Fiche produit
panier.html             Panier et redirection vers le paiement Stripe
succes.html / annule.html   Retour après paiement
cgv.html, mentions-legales.html, confidentialite.html, retours.html, livraison.html
data/products.json      ← LE CATALOGUE (prix, tailles, stock…)
images/produits/        ← VOS PHOTOS (nom du fichier = id du produit + .jpg)
assets/css/style.css    Styles et animations
assets/js/main.js       Header, footer, panier, animations
assets/js/pages.js      Logique de chaque page
netlify/functions/creer-paiement.js   Création sécurisée du paiement Stripe
```

## Lancer le site en local

Prérequis : [Node.js](https://nodejs.org) 18 ou plus récent.

```bash
npm install
npm run apercu          # aperçu rapide → http://localhost:8888 (sans paiement)
```

Pour tester aussi le paiement en local :

```bash
echo "STRIPE_SECRET_KEY=sk_test_..." > .env    # votre clé de TEST Stripe
npm run dev                                     # → http://localhost:8888
```

> Ouvrir directement `index.html` en double-cliquant ne fonctionne pas :
> le catalogue est chargé depuis `data/products.json`, ce qui nécessite un serveur.

## Mettre en ligne sur Netlify

1. Sur [app.netlify.com](https://app.netlify.com), choisissez **Add new site → Import an existing project**, puis sélectionnez ce dépôt GitHub.
   Il n’y a rien à remplir : `netlify.toml` contient déjà la configuration.
2. Dans **Site configuration → Environment variables**, ajoutez `STRIPE_SECRET_KEY` avec votre
   clé Stripe (`sk_test_…` pour tester, puis `sk_live_…` pour vendre réellement).
3. Dans **Forms**, activez la détection des formulaires. Les demandes de contact et de rachat
   arriveront alors dans votre tableau de bord Netlify, et vous pourrez être notifié par e-mail.
4. Pour utiliser votre propre domaine (par exemple maison-aurevia.fr), allez dans **Domain management**.

Testez un paiement avec la carte de test Stripe `4242 4242 4242 4242`, n’importe quelle date future et n’importe quel CVC.

## Ajouter ou modifier une pièce

Modifiez `data/products.json` :

```json
{
  "id": "dior-b22-bleu",            // unique, sans espace ni accent → nom de la photo
  "marque": "Dior",                 // Fendi, Louis Vuitton, Gucci, Dior… (ajoute le filtre automatiquement)
  "type": "Sneakers",               // Casquette, Bob ou Sneakers
  "modele": "B22",                  // facultatif (B22, B30…) → apparaît dans le filtre Produit
  "nom": "Sneakers B22",
  "couleur": "Bleu & blanc",
  "prix": 760,                      // en euros
  "etat": "Très bon état",
  "taille": "EU 42",
  "description": "…",
  "stock": 1,                       // 0 = affichée « Vendu »
  "nouveau": true,
  "date": "2026-11-10"              // sert au tri « Nouveautés »
}
```

Déposez ensuite la photo `images/produits/dior-b22-bleu.jpg`, puis committez et poussez :
Netlify redéploie automatiquement.
Les prix sont relus côté serveur au moment du paiement, ce qui empêche un client de les modifier.

Après une vente, passez `stock` à `0` (la pièce s’affiche alors « Vendu ») ou supprimez-la.

## À compléter avant l’ouverture

- [ ] Les informations entre `[crochets]` dans `cgv.html`, `mentions-legales.html` et `confidentialite.html` : SIRET, adresse, régime de TVA, médiateur de la consommation, etc. Faites relire ces pages par un professionnel.
- [ ] L’adresse e-mail `contact@maison-aurevia.fr` et le lien Instagram dans `index.html` (section contact).
- [ ] Les photos de vos pièces dans `images/produits/`.
- [ ] Le catalogue réel dans `data/products.json` : les pièces actuelles sont des exemples.

## Animations

| Effet | Où | Technique |
|---|---|---|
| Apparition au scroll (fondu + translation) | Toutes les sections (`.reveal`) | IntersectionObserver + `opacity`/`transform` |
| Header qui se compacte | Dès 60 px de scroll | Classe `.est-compact`, `transform` + fond en `opacity` |
| Dégradé animé | Fond du hero et des en-têtes | Calques de dégradés animés en `transform` (GPU) |
| Effet magnétique | Boutons `.magnetique` | `pointermove` + `requestAnimationFrame` avec lissage |
| Chiffres qui défilent | Bandeau de compteurs | `requestAnimationFrame` + easing |

Seuls `transform` et `opacity` sont animés, ce qui garantit 60 fps sans recalcul de mise en page.
Si `prefers-reduced-motion: reduce` est activé, toutes les animations sont coupées : le contenu
s’affiche directement et les compteurs montrent leur valeur finale.
L’effet magnétique ne s’active qu’avec une souris.
