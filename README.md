# curly-octo-fishstick — Graphismes Réalistes Roblox 🔥

Rend ton jeu Roblox **beaucoup plus réaliste** (lumière, ombres, brume, reflets, flou cinéma)
tout en gardant le style Roblox (avatars, grille, couleurs).

## Ce que ça ajoute
- ☀️ Lumière **Future** + style **Realistic** : vraies ombres douces, reflets, lumière indirecte
- 🌫️ **Atmosphere** : brume et profondeur à l'horizon (fini le ciel tout plat)
- ☁️ **Nuages volumétriques** + soleil/étoiles
- ✨ **Bloom**, **SunRays**, **Color Correction** (contraste + couleurs cinéma)
- 🎥 **Flou de profondeur** avec mise au point automatique sur ton perso
- 👁️ **Exposition adaptative** (comme un vrai œil : ébloui face au soleil, s'adapte à l'ombre)
- 🧱 Matériaux 2022 HD, eau réaliste, herbe animée
- ⌨️ Touche **G** pour activer/désactiver (PC faibles)

## Installation (copier‑coller dans Studio)
1. **ServerScriptService** → clic droit → *Insert Object* → **Script** → colle le contenu de
   `src/ServerScriptService/RealisticGraphics.server.lua`
2. **StarterPlayer > StarterPlayerScripts** → *Insert Object* → **LocalScript** → colle
   `src/StarterPlayerScripts/RealisticCamera.client.lua`
3. ⚠️ **Important** : sélectionne **Lighting** dans l'Explorer → Propriétés →
   **Technology = Future** (Roblox ne permet pas de le changer par script).
4. Dans le jeu : *Échap > Paramètres > Qualité graphique* → mets au **maximum (10)**
   sinon les ombres/reflets ne s'affichent pas.

Avec Rojo : `rojo serve` (le fichier `default.project.json` est déjà prêt).

## Changer l'ambiance
En haut de `RealisticGraphics.server.lua` :
```lua
local PRESET = "CleanHD"   -- "CleanHD" (net, style TikTok), "Jour", "CoucherDeSoleil" ou "Nuit"
```

## Encore plus réaliste
- Remplace les parts lisses (`SmoothPlastic`) par des matériaux comme `Concrete`, `Metal`, `Wood`…
- Ajoute des `SurfaceAppearance` (textures PBR) sur les objets importants comme l'épée.
- Ajoute des `PointLight` / `SpotLight` avec `Shadows = true` pour les lampes.
