# Reel — Comment les Tours Aillaud (Tours Nuages) de Nanterre sont nées

Vidéo verticale 1080×1920, 40 s, style motion design TikTok/Reels :
**`reel/reel_nanterre.mp4`**

Toute la vidéo est générée par du code (aucune IA vidéo) :
- `reel/reel.html` : les scènes, dessinées et animées sur un canvas
- `reel/render.js` : capture image par image avec Playwright, puis montage avec ffmpeg
- `reel/music.py` : petite musique et bruitages générés (libres de droits)

## Re-générer
```bash
cd reel && node render.js   # nécessite playwright, ffmpeg, python3 + numpy
```

## Le contenu
1. Accroche : « Ces tours à Nanterre cachent une histoire de ouf » / TOURS NUAGES
2. Années 50-60 : le bidonville de La Folie (pas d'électricité, une seule fontaine)
3. Juin 1971 : le bidonville est rasé, les familles relogées en cités de transit
4. 1973 : l'architecte Émile Aillaud reçoit la commande
5. L'idée : des tours qui se fondent dans le ciel, mosaïque en pâte de verre
6. Fenêtres rondes, carrées et en goutte d'eau
7. 18 tours, 1973 → 1981, surnom « Tours Nuages »
8. Label « Architecture contemporaine remarquable » + rénovation lancée le 18 mars 2023
9. Outro : Abonne-toi
