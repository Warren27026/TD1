# Réflexions — TD1

Réponses proposées : les préférences personnelles sont à adapter avant remise.

## 1. Avant de construire — pondération personnelle
Je retiens, pour cet exercice, 50 % pour la météo et 50 % pour les émissions. Je souhaite un séjour agréable sans ignorer le coût environnemental du trajet ; cette préférence correspond donc au compromis calculé.

## 2. Acquisition — fiabilité
Chaque connexion supplémentaire peut subir une erreur DNS, un échec TLS, un délai dépassé ou une limitation de débit. Une requête groupée réduit ces occasions de panne et la charge de connexion ; elle ne garantit toutefois pas la disponibilité de l’API, d’où les tentatives avec attente et la validation des données.

## 3. Acquisition — provenance du facteur CO₂
Avant une publication destinée à de vrais voyageurs, je chercherais le facteur officiel le plus récent, sa catégorie de vol, son unité par passager-kilomètre et son périmètre (CO₂ seul, CO₂e, effets non-CO₂, amont du carburant). Je consignerais la source exacte, l’année et les hypothèses, puis prévoirais une révision annuelle. Ici, 0,15 est conservé comme hypothèse du TP, sans prétendre qu’il s’agit d’un facteur officiel vérifié ; le calcul simplifié ne remplace pas un bilan de trajet réel.

## 4. Transformation — mesure et KPI relatif
Ajouter une capitale très froide et pluvieuse ne change pas la température mesurée ailleurs. Cela peut déplacer les bornes de normalisation et donc les scores de température et de pluie, puis le classement, même si les mesures initiales restent identiques. Un KPI dépend ainsi du groupe de comparaison et des choix de calcul ; il ne se confond pas avec une mesure physique.

## 5. KPI — prédiction avant exécution
Prédiction retenue avant la collecte : Rome pour le scénario initial au départ de Paris. Sa météo potentiellement favorable et sa distance intermédiaire pourraient produire un meilleur compromis que les destinations les plus lointaines ; il s’agit d’une hypothèse, pas d’une prévision déjà vérifiée.

## 6. Après exécution — prédiction confrontée au résultat
La collecte réelle du 21 octobre 2026 classe Madrid première au départ de Paris (score 0,756), alors que ma prédiction proposée était Rome (score 0.668). Madrid bénéficie notamment de 0 mm de pluie prévus sur la période, contre 36.9 mm à Rome : la température seule ne suffit donc pas à anticiper le score météo. Cette comparaison porte sur une exécution locale réelle ; l’exécution GitHub Actions du scénario Lyon a ensuite réussi le 21 octobre 2026 et publié le site (run 39551215894). Les chiffres de comparaison ci-dessous correspondent aux collectes locales initiales, conservées dans les preuves.

## 7. Automatisation — surveillance
Le visiteur peut regarder la date de dernière collecte : si elle cesse d’avancer, les résultats risquent de ne plus soutenir la décision du moment (CM4). Ce signal est utile mais insuffisant si personne ne le surveille ; la page ajoute une alerte lorsque la collecte dépasse huit jours ou que la période météo est terminée. Pour un service réel, j’ajouterais une alerte indépendante sur le dernier succès et les échecs, car le planificateur peut lui-même s’arrêter.

## 8. Extension — départ de Lyon
J’ai modifié `scripts/fetch_and_score.py` pour définir Lyon (45,7640 ; 4,8357), calculer les distances depuis cette origine, filtrer la ville d’origine si elle figure parmi les capitales et écrire l’origine dans le JSON. J’ai modifié `docs/index.html` pour lire ce champ et afficher le bon départ et le bon nombre de destinations ; le tableau de référence reste identique. Lyon n’étant pas une capitale de l’UE, les 27 capitales sont conservées, dont Paris.

Madrid reste première, mais son trajet passe de 1 052,9 à 912,5 km par sens, son estimation de 315,9 à 273,8 kg CO₂e aller-retour, et son score de 0,756 à 0,788. Le classement dépend donc du départ, de la météo, des destinations comparées et des pondérations : il ne décrit pas une qualité absolue d’une ville. Aucun résultat de camarade n’a été fourni ; la comparaison réalisée est celle des deux scénarios Paris/Lyon.
