/**
 * Maison Aurévia — création d'une session de paiement Stripe Checkout.
 *
 * Sécurité : le navigateur n'envoie que des identifiants et des quantités.
 * Les prix sont TOUJOURS relus ici, côté serveur, depuis data/products.json :
 * un client ne peut donc pas modifier le montant à payer.
 *
 * Variables d'environnement (Netlify > Site configuration > Environment variables) :
 *   STRIPE_SECRET_KEY  clé secrète Stripe (sk_test_… pour tester, sk_live_… en production)
 *   URL                fournie automatiquement par Netlify (adresse du site)
 */
const Stripe = require("stripe");
const produits = require("../../data/products.json");

const reponse = (statut, corps) => ({
  statusCode: statut,
  headers: { "Content-Type": "application/json; charset=utf-8" },
  body: JSON.stringify(corps),
});

exports.handler = async (event) => {
  if (event.httpMethod !== "POST") {
    return reponse(405, { erreur: "Méthode non autorisée." });
  }

  const cle = process.env.STRIPE_SECRET_KEY;
  if (!cle) {
    return reponse(500, {
      erreur: "Le paiement n’est pas encore configuré (clé Stripe manquante).",
    });
  }

  let articles;
  try {
    articles = JSON.parse(event.body || "{}").articles;
  } catch {
    return reponse(400, { erreur: "Requête invalide." });
  }
  if (!Array.isArray(articles) || articles.length === 0 || articles.length > 20) {
    return reponse(400, { erreur: "Votre panier est vide." });
  }

  const lignes = [];
  for (const article of articles) {
    const p = produits.find((x) => x.id === article?.id);
    const qte = Number.parseInt(article?.qte, 10);
    if (!p) return reponse(400, { erreur: "Une pièce de votre panier n’existe plus." });
    if (!Number.isInteger(qte) || qte < 1) return reponse(400, { erreur: "Quantité invalide." });
    if (p.stock < qte) {
      return reponse(409, { erreur: `${p.marque} ${p.nom} n’est plus disponible.` });
    }
    lignes.push({
      quantity: qte,
      price_data: {
        currency: "eur",
        unit_amount: Math.round(p.prix * 100),
        product_data: {
          name: `${p.marque} — ${p.nom}`,
          description: `${p.couleur} · ${p.taille} · ${p.etat}`,
          metadata: { id: p.id },
        },
      },
    });
  }

  const site = process.env.URL || `https://${event.headers.host}`;

  try {
    const stripe = Stripe(cle);
    const session = await stripe.checkout.sessions.create({
      mode: "payment",
      locale: "fr",
      line_items: lignes,
      shipping_address_collection: { allowed_countries: ["FR"] },
      shipping_options: [
        {
          shipping_rate_data: {
            display_name: "Livraison suivie et assurée — offerte",
            type: "fixed_amount",
            fixed_amount: { amount: 0, currency: "eur" },
            delivery_estimate: {
              minimum: { unit: "business_day", value: 2 },
              maximum: { unit: "business_day", value: 5 },
            },
          },
        },
      ],
      phone_number_collection: { enabled: true },
      consent_collection: { terms_of_service: "required" },
      custom_text: {
        terms_of_service_acceptance: {
          message: `J’accepte les [conditions générales de vente](${site}/cgv.html) de Maison Aurévia.`,
        },
      },
      metadata: { articles: articles.map((a) => `${a.id}x${a.qte}`).join(",").slice(0, 490) },
      success_url: `${site}/succes.html?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${site}/annule.html`,
    });
    return reponse(200, { url: session.url });
  } catch (e) {
    console.error("Stripe :", e.message);
    return reponse(502, { erreur: "Le paiement est momentanément indisponible. Réessayez dans un instant." });
  }
};
