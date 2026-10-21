# TD1 — Capitales européennes : météo et CO₂

## Décision soutenue
Choisir une capitale de l’Union européenne pour un séjour de sept jours, au départ de Lyon, en combinant qualité météo et émissions estimées du déplacement. Le prix est volontairement exclu. Le projet répond aux étapes 1 à 7 du manuel et inclut les huit réflexions en français.

## Résultats réellement obtenus
Collecte Open-Meteo du 21 octobre 2026 ; prévisions du 21 au 27 octobre inclus. Madrid arrive première depuis Lyon : 0,788 ; 912,5 km par sens ; 273,8 kg CO₂e aller-retour selon le modèle pédagogique. Le scénario initial Paris comporte 26 destinations et le scénario Lyon 27. Voir `evidence/COMPARAISON.md` et `evidence/paris.json` pour la comparaison des collectes locales initiales. Le JSON du site est ensuite actualisé par le workflow ; ses prévisions peuvent donc différer légèrement de cette comparaison figée. Une ville gagnante identique n’implique pas des distances ou des scores identiques.

## Chaîne BI
1. Acquisition : `data/capitals.csv` et une requête groupée Open-Meteo.
2. Transformation : agrégation de sept jours, distance de Haversine, normalisation min-max.
3. KPI : météo = moyenne des trois scores température, soleil et faible pluie ; score final = 50 % météo + 50 % faible CO₂.
4. Stockage : JSON horodaté et versionné par Git à chaque collecte.
5. Visualisation : recommandation, classement en barres, nuage de points et tableau chiffré.
6. Orchestration : lundi 06:00 UTC et lancement manuel ; validation avant remplacement du résultat, puis commit et publication.
7. Surveillance : date de collecte, période prévue et alerte de données périmées.

## Mise en ligne vérifiée
- Dépôt public : https://github.com/Warren27026/TD1_Business_intelligence
- Tableau de bord : https://warren27026.github.io/TD1_Business_intelligence/
- Exécution réussie : https://github.com/Warren27026/TD1_Business_intelligence/actions/runs/39551215894
- JSON public vérifié : collecte du 21 octobre 2026 à 05:44:09 UTC, 27 capitales et origine Lyon.
- Contrôles locaux réussis : distances, normalisation, scores, tri, exclusion de l’origine et syntaxe JavaScript ; les deux graphiques ont été vérifiés dans le navigateur.

## Reproduire la publication
1. Créer un dépôt public `eu-capitals-dashboard`, branche `main`.
2. Déposer le contenu de ce dossier à la racine, y compris `.github/workflows/update-data.yml`. Ne pas déposer seulement le ZIP ni un dossier englobant.
3. Le workflow déclare explicitement `contents: write`, `pages: write` et `id-token: write`. Il fonctionne avec ces permissions ciblées ; aucun élargissement global des droits par défaut n’est nécessaire.
4. Settings → Pages → Source : **GitHub Actions**.
5. Actions → Update capitals ranking → Run workflow sur `main`.
6. Attendre le succès du job, vérifier le nouveau JSON et ouvrir l’URL Pages fournie par le déploiement.
7. Remettre l’URL réelle du dépôt, l’URL Pages vérifiée et `REFLECTIONS.md`.

Les préférences et la prédiction de `REFLECTIONS.md` sont des réponses proposées à relire et personnaliser.

## Écart technique justifié par rapport au manuel
Le manuel propose Pages depuis `main/docs` ; GitHub indique cependant que les commits effectués avec `GITHUB_TOKEN` ne déclenchent pas de build Pages. Le workflow fourni publie donc explicitement `docs` avec les actions officielles de Pages ; choisir **GitHub Actions** comme source. Le dossier publié reste `docs` et les données restent commitées. Autre simplification : le script utilise la bibliothèque standard Python (`urllib`) à la place de `requests`, sans installation supplémentaire.

## Exécution locale (Python 3.12 ou plus récent)
```sh
python scripts/fetch_and_score.py
python scripts/fetch_and_score.py --origin Paris --output evidence/paris.json
python -m http.server 8000 --directory docs
```
Ouvrir http://localhost:8000 pour le tableau de bord. La commande Paris n’écrase pas le classement Lyon. Le fichier `APERCU.html` livré à côté du dossier est un aperçu figé, ouvrable directement ; les graphiques nécessitent l’accès au CDN Chart.js. Il ne se met pas à jour automatiquement.

## Hypothèses et limites
- Facteur 0,15 kg CO₂e/passager-km repris du TP comme hypothèse, sans validation officielle ; aucune garantie sur le périmètre des effets non-CO₂.
- Distance à vol d’oiseau entre centres-villes, et non distance réelle de vol ; ni escales, ni train, ni disponibilité de liaisons.
- Le min-max est relatif aux destinations présentes ; les scores ne sont pas directement comparables entre semaines.
- Une température plus élevée est toujours favorisée, y compris lorsqu’elle serait inconfortable.
- Sept jours à partir du jour de collecte, conformément à `forecast_days=7` ; il ne s’agit pas strictement de la semaine civile suivante.
- En cas d’échec ou de valeurs météo manquantes, le script échoue sans écraser le dernier fichier valide.
- Les heures affichées dans `generated_at` sont en UTC ; 06:00 UTC vaut 07:00 à Paris en hiver et 08:00 en été.

## Sources
- Manuel TD1 fourni : coordonnées, calcul et facteur pédagogique.
- Cours fourni : *Business Intelligence*, ENSIM, 2026, chapitres 1 à 4 (décision, KPI, provenance, automatisation).
- [API Open-Meteo](https://open-meteo.com/en/docs), données sous [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- [Publication Pages et limite de GITHUB_TOKEN](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).
- [Workflow Pages explicite](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).
- [Désactivation des workflows après inactivité](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/disable-and-enable-workflows).
