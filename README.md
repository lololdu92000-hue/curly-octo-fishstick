# Reel — Comment les Tours Aillaud (Tours Nuages) de Nanterre sont nées

Vidéo verticale 1080×1920, 48 s, style motion design TikTok/Reels :
**`reel/reel_nanterre.mp4`**

Toute la vidéo est générée par du code (aucune IA vidéo) :
- `reel/reel.html` : les scènes, dessinées et animées sur un canvas
- `reel/render.js` : capture image par image avec Playwright, puis montage avec ffmpeg
- `reel/music.py` : petite musique et bruitages générés (libres de droits)

## Re-générer
```bash
cd reel && node render.js   # nécessite playwright, ffmpeg, python3 + numpy
```

## Le contenu (v2)
1. Accroche : TOURS NUAGES au coucher du soleil, tours 3D avec lumière, reflets et ombres
2. Archive façon vieux film (sépia, grain) : le bidonville de La Folie, années 50-60
3. Juin 1971 : un bulldozer rase le bidonville, familles relogées en cités de transit
4. 1973 : plan d'architecte animé, Émile Aillaud reçoit la commande
5. Chantier en accéléré avec grue, compteur 1973 → 1981
6. Zoom arrière depuis les carreaux de mosaïque jusqu'à la tour entière
7. Fenêtres rondes, carrées et en goutte d'eau
8. Les 18 tours numérotées, surnom « Tours Nuages »
9. Passage du jour à la nuit, label + rénovation lancée le 18 mars 2023
10. Fin : « ON FAIT QUELLE VILLE MAINTENANT ? » avec sondage et commentaire

Le rendu utilise un flou de mouvement (3 sous-images par image) et un étalonnage grain + vignettage.
Après `node render.js`, recompresser : `ffmpeg -i reel_nanterre_raw.mp4 -crf 22 -c:a copy reel_nanterre.mp4`.

## Voix off
`reel/reel_nanterre_FINAL.mp4` = la version finale avec la voix ElevenLabs « Emilio », phrase par phrase calée sur chaque scène. (Ancien essai : voix Piper « siwis » abaissée vers ~160 Hz
pour un timbre de garçon un peu aigu, effet micro léger) et la musique qui baisse automatiquement quand la voix parle.
Script : `reel/voix_off.py` (nécessite `pip install piper-tts` et le modèle `voice-fr-siwis-medium` des releases GitHub de rhasspy/piper v0.0.2).
