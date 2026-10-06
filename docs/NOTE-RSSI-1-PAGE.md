# HR Analytics — note de validation pour le RSSI

**Version 1.0.0 · octobre 2026 · outil interne d'analyse de rémunération**

Cette note tient en une page pour que la vérification de conformité se fasse
sans lire le dossier complet. Le dossier détaillé (`DOSSIER-RSSI.md`) et le
code source complet accompagnent le livrable.

---

## Ce qu'est l'outil

Une application de bureau Windows. L'utilisateur ouvre un fichier RH (.xlsx
ou .csv) depuis son poste, l'outil calcule des indicateurs de rémunération et
produit des documents dans un dossier que l'utilisateur désigne. Rien d'autre.

Pas de serveur. Pas de service. Pas de compte. Pas d'installation. Pas de
droits administrateur. Aucun accès à nos systèmes n'est nécessaire pour le
valider : tout est dans l'archive fournie.

---

## Les six points à confronter à la politique

| # | Point | État | Comment le vérifier |
|---|---|---|---|
| 1 | **Accès réseau** | **Impossible, pas seulement absent** | `runtime\python.exe -I -c "import socket"` → `ModuleNotFoundError`. La pile réseau est retirée de l'interpréteur livré |
| 2 | **OneDrive / SharePoint / cloud** | **Jamais contacté** | Conséquence directe du point 1. Voir la réserve ci-dessous |
| 3 | **Shell / CMD / PowerShell** | **Jamais invoqué** | Analyse syntaxique : 0 appel. Exécution complète instrumentée : 0 tentative |
| 4 | **Élévation de privilège** | **Impossible** | Aucun manifeste d'élévation dans les deux exécutables. Tourne avec les droits de l'utilisateur |
| 5 | **Registre Windows, services, tâches planifiées, persistance** | **Aucun** | Aucune API de registre dans la table d'import du lanceur |
| 6 | **Dépendances tierces** | **Aucune** | Bibliothèque standard Python uniquement. Aucun flux de CVE tierces à suivre |

---

## Où l'outil écrit — la liste complète

Mesuré en instrumentant chaque ouverture de fichier pendant une analyse
complète : **34 écritures, dont 0 hors des dossiers désignés par
l'utilisateur.**

| Emplacement | Contenu |
|---|---|
| Le dossier que l'utilisateur choisit pour les documents | Rapport HTML, synthèse, vue détaillée, classeur Excel |
| `config\` à côté de l'outil (ou `%LOCALAPPDATA%\HR Analytics\config` pour la forme fichier unique) | 10 fichiers de réglages, en texte |
| `journal\technical.log` | Journal technique. **Vérifié : aucune donnée personnelle** |

Rien ailleurs. Pas de `%TEMP%`, pas de `%APPDATA%\Roaming`, pas de dossier
système.

---

## La seule réserve, et elle est importante

**L'outil ne contacte jamais OneDrive. Mais il ne peut pas empêcher OneDrive
de faire son travail.**

Si l'utilisateur enregistre les documents dans un dossier synchronisé
(Bureau, Documents, ou le dossier OneDrive lui-même — fréquent avec la
redirection de dossiers connus), **le classeur Excel partira dans le cloud**.
Ce n'est pas l'outil qui l'envoie : c'est la synchronisation du poste.

Cela compte, parce que **le classeur Excel contient les données
individuelles** — noms, matricules, montants. C'est sa fonction : il sert à
retravailler les chiffres. Les autres documents (rapport, synthèse, vue
détaillée) n'en contiennent aucune, c'est mesuré.

**Deux traitements possibles, au choix de la politique :**

1. Consigner dans la procédure d'usage un dossier de destination non
   synchronisé (par exemple un lecteur réseau RH à accès restreint) ;
2. Ou décocher la production du classeur Excel quand elle n'est pas nécessaire :
   les trois autres documents ne portent aucune identité.

À noter : `%LOCALAPPDATA%`, où la forme fichier unique dépose ses fichiers,
**n'est pas synchronisé** par OneDrive.

---

## Protection des documents produits

Chaque document est restreint à son propriétaire après écriture. **Sous
Windows, cette protection repose en pratique sur les droits NTFS du dossier
de destination**, pas sur le logiciel : si les documents sont écrits dans un
partage, ce sont les ACL du partage qui décident.

---

## Deux points ouverts, qui relèvent de votre décision

1. **L'exécutable n'est pas signé.** SmartScreen avertira au premier
   lancement. Une signature avec le certificat interne de l'entreprise lève
   l'avertissement sur le parc, sans coût. La procédure est dans le dossier
   détaillé.

2. **Deux formes de livraison existent.** Nous recommandons **la forme
   dossier**. La forme fichier unique se déballe sur le disque avant de
   s'exécuter — comportement légitime, mais surveillé par les protections de
   poste. La forme dossier ne le fait pas : tout y est déjà en clair.

---

## Pour une mise en liste d'autorisation

| Demandé | Fourni |
|---|---|
| SHA-256 de chaque fichier | `docs\EMPREINTES-RUNTIME.txt`, dans l'archive |
| Éditeur, produit, version | Dans les propriétés du fichier |
| Arbre de processus attendu | `HR Analytics.exe` → `pythonw.exe`, rien d'autre |
| Destinations réseau attendues | **aucune** |
| Code source | Dans l'archive, lanceur C compris |

Une autorisation **par empreinte** est préférable à une autorisation par
chemin : elle ne survit pas à une modification du binaire.

---

## Ce que nous ne garantissons pas

Aucun logiciel n'est exempt de défauts, et nous n'affirmons pas le contraire.
Ce qui est établi, c'est que **la surface d'attaque se limite à un fichier
tableur que l'utilisateur ouvre lui-même** : pas de port à l'écoute, pas de
service, pas d'entrée réseau, pas d'élévation. Les trois classes d'attaque
connues sur ce format de fichier (bombe à entités XML, entité externe, bombe
ZIP) sont testées et bloquées, par des essais qui construisent réellement les
fichiers hostiles et les soumettent à l'outil.

Un audit mené avant cette livraison a trouvé et corrigé cinq défauts, dont
une garde XML qui ne s'appliquait pas au bon endroit et une affirmation de
notre documentation qui s'est révélée fausse au contrôle. Ils sont listés au
§10 du dossier détaillé. Un dossier qui ne dit que les bonnes nouvelles n'a
aucune valeur.
