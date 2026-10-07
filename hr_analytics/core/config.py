"""Chargement et fusion des parametres.

Les parametres vivent dans des fichiers JSON locaux (`config/`), jamais dans
le code. JSON est retenu plutot que YAML/SQLite : lisible par un RH, editable
sans outil, parse par la bibliotheque standard (aucune dependance a installer,
aucun binaire a faire valider par l'IT).

Toute valeur absente d'un fichier utilisateur retombe sur le defaut embarque :
le logiciel demarre donc meme sans dossier `config/`.
"""

from __future__ import annotations

import copy
import json
import os
from typing import Any, Dict, List, Optional

from .errors import ConfigError

CONFIG_FILES = (
    "population_mapping",
    "age_parameters",
    "tenure_parameters",
    "percentile_parameters",
    "salary_parameters",
    "privacy_parameters",
    "pay_equity_parameters",
    "chart_parameters",
    "theme_parameters",
    "export_parameters",
    "package_parameters",
    "career_parameters",
)

DEFAULTS: Dict[str, Any] = {
    "population_mapping": {
        # champ normalise -> libelles acceptes dans le fichier source
        "fields": {
            "employee_id": ["Matricule", "Employee ID", "ID"],
            "last_name": ["Nom", "Last name"],
            "first_name": ["Prénom", "First name"],
            "gender": ["Sexe", "Genre", "Gender"],
            "birth_date": ["Date de naissance", "Birth date"],
            "hire_date": ["Date d'entrée", "Date début", "Date de début",
                          "Date d'embauche", "Hire date"],
            "leave_date": ["Date de sortie", "Date de fin", "Leave date"],
            # Le jour ou la paie a ete extraite. Il n'entre dans aucun
            # calcul de remuneration : il ancre la periode proposee pour
            # les elements variables, qui doit s'achever au plus pres de
            # l'extraction du salaire.
            "extraction_date": ["Date d'extraction", "Date_d_extraction",
                                "Extraction date"],
            "business_unit": ["BU", "Business Unit"],
            "country": ["Pays", "Country"],
            "site": ["Établissement", "Site"],
            "job": ["Métier", "Job"],
            "job_title": ["Poste", "Intitulé de poste", "Job title", "Position"],
            # Periode d'observation. Facultative : sans elle, le fichier est
            # un instantane et l'outil se comporte comme avant. Avec elle,
            # un meme salarie peut figurer plusieurs fois — une ligne par
            # periode — et l'identite devient le couple matricule + periode.
            "period": ["Période", "Periode", "Period", "Date d'effet",
                       "Mois", "Année", "Annee"],
            # Matricule du responsable hierarchique. Facultatif : avec lui,
            # l'arbre se reconstruit du plus haut au plus bas, et l'equipe
            # d'un manager devient une population analysable.
            "manager": ["Manager", "Responsable", "Manager ID",
                        "Matricule manager", "N+1"],
            "job_family": ["Famille métier", "Job family"],
            # La classification conventionnelle francaise. Une convention
            # collective classe un poste par une annexe (le metier ou la
            # filiere), un groupe (le niveau) et un coefficient (le point
            # d'indice). « Grade » n'est le mot d'aucune d'entre elles :
            # c'est un terme d'entreprise, qui ne se retrouve pas d'un
            # fichier de paie a l'autre.
            "annexe": ["Annexe", "Filière", "Filiere"],
            "groupe": ["Groupe", "Niveau", "Classe"],
            "coefficient": ["Coefficient", "Indice"],
            "status": ["Statut", "Status"],
            # « Tx Activité » est l'ecriture des paies francaises, en
            # pourcentage sans le signe : 100, 80. L'echelle se devine a
            # la valeur, personne ne travaillant a cinquante fois le
            # temps plein.
            "fte": ["Temps de travail", "Tx Activité", "Taux d'activité",
                    "Taux activité", "FTE"],
            "base_salary": ["Salaire de base", "Base salary"],
            "variable_pay": ["Variable", "Variable pay"],
            "total_compensation": ["Rémunération totale"],
        },
        # Dimensions d'analyse : elles servent partout de la meme facon —
        # critere de selection, axe de segmentation, couleur du nuage.
        # Ajouter une notion metier (equipe, manager, direction) se fait ici
        # et dans "fields", sans modification du code.
        "dimensions": [
            {"field": "business_unit", "label": "BU"},
            {"field": "country", "label": "Pays"},
            {"field": "site", "label": "Établissement"},
            {"field": "job", "label": "Métier"},
            {"field": "job_title", "label": "Poste"},
            {"field": "job_family", "label": "Famille métier"},
            {"field": "annexe", "label": "Annexe"},
            {"field": "groupe", "label": "Groupe"},
            {"field": "coefficient", "label": "Coefficient"},
            {"field": "status", "label": "Statut"},
            {"field": "gender", "label": "Sexe"},
            {"field": "age_band", "label": "Tranche d'âge"},
            {"field": "tenure_band", "label": "Tranche d'ancienneté"},
        ],
        # Colonnes exigees en plus du champ d'analyse, que le moteur
        # ajoute toujours (voir `mapping.required_fields`). La liste est
        # vide : l'outil n'impose qu'une colonne, celle qui porte la
        # remuneration analysee. Une organisation qui veut imposer sa
        # propre discipline — un matricule, un etablissement — l'ecrit
        # ici. Sans matricule, le controle qualite dit que le suivi des
        # doublons n'est pas possible, et l'analyse se poursuit.
        "required": [],
        "numeric": ["coefficient", "fte", "base_salary", "variable_pay", "total_compensation"],
        # Parmi les champs numeriques, ceux qui portent un montant. Ils
        # s'ecrivent en monnaie dans les exports et recoivent une colonne
        # dans l'onglet des donnees individuelles. « coefficient » et
        # « fte » sont numeriques sans etre des montants : ecrits en euros
        # ils ne voudraient rien dire.
        "money": ["base_salary", "variable_pay", "total_compensation"],
        "date": ["birth_date", "hire_date", "leave_date",
                 "extraction_date"],
        "personal": ["last_name", "first_name", "birth_date", "employee_id"],
        # Encodages essayes a la lecture d'un CSV, dans l'ordre. Voir
        # `tabular.DEFAULT_ENCODINGS` : l'ordre compte, l'UTF-8 doit venir
        # en premier parce qu'il est le seul a echouer franchement.
        "encodings": ["utf-8-sig", "cp1252"],
        # Au-dela de ce nombre de valeurs distinctes, une liste deroulante
        # n'est plus utilisable : la dimension reste analysable, mais n'est
        # pas proposee comme filtre dans l'interface.
        "max_filter_values": 200,
        # Plafond de ce qu'un classeur a le droit de peser une fois
        # decompresse, en megaoctets. Un .xlsx est une archive : trois
        # megaoctets sur le disque peuvent en faire trois mille en memoire,
        # et le systeme tue alors le processus sans un mot. Mesure : un
        # onglet de 200 000 salaries pese 149 Mo decompresse.
        "max_uncompressed_mb": 512,
    },
    "age_parameters": {
        "bands": [
            {"label": "20-29", "min": 20, "max": 29, "max_inclusive": True},
            {"label": "30-39", "min": 30, "max": 39, "max_inclusive": True},
            {"label": "40-49", "min": 40, "max": 49, "max_inclusive": True},
            {"label": "50-59", "min": 50, "max": 59, "max_inclusive": True},
            {"label": "60+", "min": 60, "max": None},
        ],
        # Meme mecanisme que pour l'anciennete, desactive par defaut : la
        # tranche « 60+ » recouvre une realite, alors que « > 10 ans »
        # d'anciennete n'en recouvre pas une.
        "auto_extend": False,
        "extend_step": 10,
        "band_label": "{low}-{high}",
        "open_band_label": "{low}+",
        "reference_date": None,
    },
    "tenure_parameters": {
        "bands": [
            {"label": "<2 ans", "min": 0, "max": 2},
            {"label": "2-5 ans", "min": 2, "max": 5},
            {"label": "5-10 ans", "min": 5, "max": 10},
            {"label": ">10 ans", "min": 10, "max": None},
        ],
        # Une derniere tranche « > 10 ans » range ensemble une anciennete de
        # 11 ans et une de 30 : la comparaison n'a plus de sens des que la
        # population contient des carrieres longues. Les tranches suivantes
        # sont donc engendrees au pas ci-dessous, jusqu'a couvrir
        # l'anciennete reellement observee — et seulement si elle depasse.
        "auto_extend": True,
        "extend_step": 5,
        "extend_max_bands": 10,
        "band_label": "{low}-{high} ans",
        "open_band_label": ">{low} ans",
        "reference_date": None,
    },
    "percentile_parameters": {
        "percentiles": [10, 25, 50, 75, 90],
    },
    "salary_parameters": {
        "analysis_field": "base_salary",
        "currency": "EUR",
        "min_plausible": 1000.0,
        "max_plausible": 1000000.0,
    },
    "privacy_parameters": {
        "min_headcount_publish": 5,
        "min_headcount_warning": 10,
        "min_headcount_chart": 10,
        # L'onglet « Organigramme » ne masque rien par defaut, et c'est une
        # decision : cette page ne sort jamais de l'ecran — aucun document,
        # aucun export, aucun journal — et elle porte sur une equipe que son
        # lecteur vient de designer. Masquee, elle serait inutilisable : un
        # poste tenu par trois personnes n'aurait ni minimum, ni mediane, ni
        # maximum. A vrai, le seuil de publication s'y applique comme
        # partout — ce que veut une installation partagee.
        "mask_in_org_chart": False,
        "anonymise_identifiers": True,
        # Sel des references anonymes. Vide : il est tire au hasard a chaque
        # analyse, et les references ne valent que dans les documents d'une
        # meme execution — c'est le reglage le plus protecteur. Renseigne,
        # les references deviennent stables d'une analyse a l'autre sur ce
        # poste, ce qui permet de suivre une situation d'une periode a la
        # suivante ; seul celui qui detient ce fichier de parametres peut
        # alors les rapprocher d'un matricule. Ne le communiquez pas avec
        # les documents produits.
        "anonymisation_salt": "",
        # Identifier un salarie a l'ecran est le geste meme de l'analyse :
        # un point du nuage a trente pour cent sous la mediane ne veut rien
        # dire tant qu'on ne sait pas de qui il s'agit. Le paragraphe 6
        # exige des identifiants *anonymisables*, pas anonymises : le
        # reglage existe, et il ne porte que sur l'ecran. Aucun document
        # produit, aucun export, aucun journal n'en depend.
        "show_identities_on_screen": True,
    },
    # Le second fichier : les elements de paie qui s'ajoutent au salaire
    # de base. Il est en lignes et non en colonnes, parce que le nombre
    # d'elements change d'une entreprise a l'autre et d'une annee a
    # l'autre : en colonnes, chaque nouvelle prime casserait le mapping.
    "package_parameters": {
        "fields": {
            # Le matricule fait la jointure : sans lui, rien a rapprocher.
            "employee_id": ["Matricule", "Employee ID", "ID"],
            "label": ["Intitulé", "Libellé", "Élément", "Rubrique",
                      "Nature", "Label"],
            "amount": ["Montant", "Valeur", "Amount"],
            # Facultative. Quand elle est la, l'ecran propose les bornes
            # qu'elle porte ; c'est un humain qui les confirme, parce
            # qu'un fichier ne sait pas ce qu'il ne contient pas.
            "day": ["Date", "Date de versement", "Date de paie"],
        },
        # Intitule -> nature, rempli par l'ecran de parametrage. Vide au
        # depart : les intitules d'un fichier de paie ne se devinent pas,
        # et l'outil n'en invente aucun.
        "natures": {},
    },
    # Le troisieme fichier : l'historique d'un salarie, une ligne par
    # periode. Deux colonnes seulement sont reconnues d'avance — qui et
    # quand ; toutes les autres se classent a l'ecran, parce qu'une
    # colonne de people review ne porte le meme nom nulle part.
    "career_parameters": {
        "fields": {
            "employee_id": ["Matricule", "Employee ID", "ID"],
            "period": ["Période", "Periode", "Année", "Exercice", "Date",
                       "Campagne"],
        },
        # Libelle de colonne -> role : montant, appreciation, ignoree.
        # Vide au depart : l'outil n'invente aucun intitule.
        "columns": {},
        # Maille de comparaison de la fiche. Le poste par defaut : c'est
        # a lui qu'on compare une remuneration, pas a l'entreprise.
        "comparison_field": "job_title",
    },
    "pay_equity_parameters": {
        # Les valeurs designant le sexe ne sont pas codees dans le moteur :
        # un fichier RH ecrit « F/H », « F/M » ou « Femme/Homme » selon
        # l'outil qui l'a produit. La comparaison ignore casse et accents.
        "gender_field": "gender",
        "female_values": ["F", "Femme", "Female", "W", "Mme"],
        "male_values": ["H", "M", "Homme", "Male", "Mr"],
        "variable_field": "variable_pay",
        # Categorie de « travail de meme valeur » au sens de la directive.
        "category_field": "job_title",
        # Seuil au-dela duquel la directive 2023/970 impose une evaluation
        # conjointe, faute de justification par des criteres objectifs.
        "gap_alert_threshold": 5.0,
        # Seuil de probabilite en deca duquel un ecart est dit
        # significatif : la chance qu'un ecart de cette ampleur apparaisse
        # alors que les deux sexes sont payes pareil. Cinq pour cent est
        # l'usage. Ce reglage ne masque rien et ne change aucun calcul : il
        # ne commande que le classement des postes et la mention affichee.
        "significance_level": 0.05,
        "quartile_count": 4,
        # Variables comparees entre les sexes sur la fiche d'un poste. Un
        # ecart de remuneration ne se lit pas seul : la meme difference
        # n'appelle pas la meme reponse selon que les deux sexes ont la
        # meme anciennete ou non. La liste est declarative — une prime
        # propre a l'entreprise s'y ajoute sans toucher au moteur.
        # « kind » commande la mise en forme et la nature de l'ecart :
        # « money » un pourcentage, « years » et « ratio » une difference.
        # Colonnes de la liste nominative de la page des ecarts. Elles se
        # declarent ici : ajouter « Direction » ou retirer le site ne
        # demande aucune modification du code. « width » commande la
        # largeur a l'ecran, et l'alignement qui en decoule.
        "people_columns": [
            {"field": "last_name", "label": "Nom", "width": 160},
            {"field": "first_name", "label": "Prénom", "width": 140},
            {"field": "gender", "label": "Sexe", "width": 70},
            {"field": "job_title", "label": "Poste", "width": 210},
            {"field": "business_unit", "label": "BU", "width": 130},
            {"field": "site", "label": "Établissement", "width": 150},
            {"field": "annexe", "label": "Annexe", "width": 110},
            {"field": "groupe", "label": "Groupe", "width": 90},
            {"field": "coefficient", "label": "Coefficient", "width": 100},
            {"field": "base_salary", "label": "Salaire de base",
             "width": 140},
        ],
        "profile_fields": [
            {"field": "base_salary", "label": "Salaire de base",
             "kind": "money"},
            {"field": "variable_pay", "label": "Part variable",
             "kind": "money"},
            {"field": "total_compensation", "label": "Rémunération totale",
             "kind": "money"},
            {"field": "tenure_years", "label": "Ancienneté", "kind": "years"},
            {"field": "age_years", "label": "Âge", "kind": "years"},
            {"field": "fte", "label": "Temps de travail", "kind": "ratio"},
        ],
    },
    "chart_parameters": {
        "histogram_bins": 20,
        "scatter_x": "tenure_years",
        "scatter_y": "base_salary",
        "scatter_color_by": "business_unit",
        "scatter_max_points": 5000,
        # Nombre de modalites coloriees avant regroupement dans « Autres ».
        # Au-dela de la serie categorielle, les couleurs se recyclent et
        # deux modalites deviennent indiscernables.
        "scatter_max_groups": 9,
        # Champ de la repartition en camembert, sur la vue d'ensemble. Le
        # statut porte la CSP dans la plupart des exports francais — cadre,
        # agent de maitrise, ouvrier / employe — mais c'est un parametre :
        # un fichier qui range la CSP ailleurs pointe sa colonne ici.
        "csp_field": "status",
        # Au-dela, la queue des modalites est regroupee sous « Autres ». Un
        # camembert a quinze parts ne se lit plus, et les plus petites n'ont
        # meme plus la place d'un libelle.
        "csp_max_slices": 6,
        # La droite de tendance est issue de la meme regression que le R2,
        # retire parce qu'il n'apprenait rien. La tracer sans lui reviendrait
        # a affirmer une tendance sans permettre d'en juger la solidite.
        "show_trend_line": False,
        # Ouverture de grille (Q3/Q1) a partir de laquelle la dispersion
        # merite un regard, puis une alerte. Une regle de lecture se
        # parametre : elle n'a pas sa place dans un graphique.
        "spread_alert_threshold": 1.4,
        "spread_critical_threshold": 1.8,
    },
    "theme_parameters": {
        # Nom du theme applique a l'ecran et aux documents. Un nom inconnu
        # retombe sur le theme d'origine plutot que d'ouvrir l'outil sans
        # couleurs.
        "theme": "auroral",
        # Couleur d'accent, si l'on ne veut pas celle du theme : « #8c2f4a »,
        # ou vide pour garder la sienne. Elle est refusee — et l'accent du
        # theme garde — si le blanc n'y est pas lisible : c'est la couleur
        # sur laquelle s'ecrit le bouton principal.
        "accent": "",
        # Duree minimale d'affichage de l'ecran d'accueil, en secondes.
        # Zero : pas d'ecran d'accueil, la fenetre s'ouvre directement.
        "splash_seconds": 3.0,
    },
    "export_parameters": {
        "output_directory": "output",
        "excel_enabled": True,
        "html_report_enabled": True,
        # Restitutions paysage : synthese d'une page et jeu de slides.
        "slides_html_enabled": True,
        "slides_pdf_enabled": True,
        "summary_enabled": True,
        # Donnees individuelles et recopie du fichier importe. Elles
        # etaient desactivees par defaut, au nom du traitement des donnees
        # RH ; elles sont desormais posees, parce que le classeur a une
        # raison d'etre precise : permettre a une equipe C&B de refaire
        # chaque indicateur. Un classeur d'agregats demande de croire
        # l'outil sur parole, et une verification qui suppose d'abord de
        # trouver un fichier de configuration n'est pas une verification
        # qu'on fait.
        #
        # Ce que cela implique est ecrit dans le classeur lui-meme, en tete
        # de la Synthese : les references y sont anonymisees, mais l'onglet
        # du fichier importe porte le fichier tel qu'il est arrive, noms
        # compris. Les deux reglages restent la pour qui veut un classeur
        # d'agregats seuls.
        # L'onglet « Formules » dit en toutes lettres ce que chaque
        # indicateur calcule. C'est utile en comite, et c'est de la prose :
        # il ne parait que si on le demande. Les onglets de controle, eux,
        # sont toujours la — une formule est une donnee, pas un commentaire.
        "include_method_sheet": False,
        "include_individual_data": True,
        "include_source_file": True,
        # Au-dela, le fichier importe n'est pas recopie : un classeur de
        # plusieurs centaines de milliers de lignes ne s'ouvre plus.
        "source_max_rows": 50000,
        # Au-dela, le controle par segment n'est plus pose : le classeur
        # mettrait plusieurs minutes a s'ouvrir.
        "control_max_rows": 20000,
    },
}


class Configuration:
    """Vue en lecture sur l'ensemble des parametres charges."""

    def __init__(self, data: Dict[str, Any]):
        self._data = data

    def section(self, name: str) -> Dict[str, Any]:
        if name not in self._data:
            raise ConfigError(
                f"La section de configuration \"{name}\" est introuvable.",
                technical=f"unknown config section: {name}",
            )
        return self._data[name]

    def get(self, path: str, default: Any = None) -> Any:
        """Acces pointe : `config.get("salary_parameters.currency")`."""
        node: Any = self._data
        for part in path.split("."):
            if not isinstance(node, dict) or part not in node:
                return default
            node = node[part]
        return node

    def number(self, path: str, default: Any, minimum: Optional[float] = None,
               maximum: Optional[float] = None, integer: bool = False) -> Any:
        """Parametre numerique, verifie a la lecture.

        Un fichier de parametres se corrige au bloc-notes : il s'y glisse un
        texte a la place d'un nombre, un zero la ou il faut au moins un. Lus
        sans controle, ces deux-la donnaient l'un une trace Python illisible
        (`int('beaucoup')`), l'autre une analyse silencieusement fausse — un
        seuil de publication a zero publie les segments d'une personne.

        La valeur absente retombe sur le defaut ; la valeur presente mais
        inutilisable est refusee, en nommant le fichier, la cle et ce qui a
        ete lu. Aucune donnee RH n'entre dans ce message : un parametre
        n'en contient pas.
        """
        brut = self.get(path, None)
        if brut is None or brut == "":
            brut = default
        if isinstance(brut, bool) or not isinstance(brut, (int, float, str)):
            raise self._refus(path, brut, minimum, maximum, integer)
        if isinstance(brut, str):
            try:
                brut = float(brut.replace(",", ".").strip())
            except ValueError:
                raise self._refus(path, brut, minimum, maximum, integer) from None
        if integer and float(brut) != int(brut):
            raise self._refus(path, brut, minimum, maximum, integer)
        valeur = int(brut) if integer else float(brut)
        if minimum is not None and valeur < minimum:
            raise self._refus(path, brut, minimum, maximum, integer)
        if maximum is not None and valeur > maximum:
            raise self._refus(path, brut, minimum, maximum, integer)
        return valeur

    @staticmethod
    def _refus(path: str, brut: Any, minimum: Optional[float],
               maximum: Optional[float], integer: bool) -> ConfigError:
        section = path.split(".")[0]
        nature = "entier" if integer else "nombre"
        bornes = ""
        if minimum is not None and maximum is not None:
            bornes = f" compris entre {minimum:g} et {maximum:g}"
        elif minimum is not None:
            bornes = f" supérieur ou égal à {minimum:g}"
        elif maximum is not None:
            bornes = f" inférieur ou égal à {maximum:g}"
        return ConfigError(
            f"Le paramètre \"{path}\" doit être un {nature}{bornes}. "
            f"Valeur lue : \"{brut}\". Corrigez {section}.json.",
            technical=f"invalid numeric setting: {path}={brut!r}",
        )

    def as_dict(self) -> Dict[str, Any]:
        return copy.deepcopy(self._data)


def analysis_field(config: "Configuration") -> str:
    """Champ de remuneration analyse, valide contre le mapping.

    Sans ce controle, pointer `analysis_field` sur une colonne texte faisait
    echouer le controle qualite sur une comparaison str/int — une trace
    technique illisible pour un utilisateur RH.
    """
    field_name = config.get("salary_parameters.analysis_field", "base_salary")
    numeric = config.get("population_mapping.numeric", []) or []
    if field_name not in numeric:
        raise ConfigError(
            f"Le champ d'analyse \"{field_name}\" n'est pas un champ "
            "numérique. Corrigez \"analysis_field\" dans "
            "salary_parameters.json. Champs numériques disponibles : "
            f"{', '.join(numeric)}.",
            technical=f"analysis_field not numeric: {field_name}",
        )
    return field_name


def percentiles(config: "Configuration") -> List[float]:
    """Percentiles a publier, valides."""
    configured = config.get("percentile_parameters.percentiles", []) or []
    result: List[float] = []
    for entry in configured:
        try:
            rank = float(entry)
        except (TypeError, ValueError):
            raise ConfigError(
                f"La valeur de percentile \"{entry}\" n'est pas un nombre. "
                "Corrigez percentile_parameters.json.",
                technical=f"non numeric percentile: {entry!r}",
            ) from None
        if not 0 <= rank <= 100:
            raise ConfigError(
                f"Le percentile {entry} est hors de la plage 0-100. "
                "Corrigez percentile_parameters.json.",
                technical=f"percentile out of range: {rank}",
            )
        result.append(rank)
    return result or [10.0, 25.0, 50.0, 75.0, 90.0]


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    result = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def default_config_dir() -> str:
    """Dossier de configuration a utiliser quand aucun n'est impose.

    Un simple "config" relatif designe le repertoire courant : l'outil
    lance depuis un autre dossier repartait alors sur les defauts embarques
    sans le dire, et le parametrage enregistre semblait perdu.

    On retient donc, dans l'ordre : un "config" present dans le repertoire
    courant — c'est ce qui permet de garder un parametrage par dossier de
    travail — sinon celui qui accompagne l'outil.
    """
    local = os.path.abspath("config")
    if os.path.isdir(local):
        return local

    # `__file__` vaut ".../hr_analytics/core/config.py", et dans
    # une archive .pyz le prefixe est l'archive elle-meme : on remonte
    # jusqu'au premier dossier reel.
    base = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    while base and not os.path.isdir(base):
        parent = os.path.dirname(base)
        if parent == base:
            break
        base = parent
    return os.path.join(base, "config")


def load_configuration(config_dir: str | None = None) -> Configuration:
    """Charge `config/*.json` en surcharge des defauts embarques."""
    data = copy.deepcopy(DEFAULTS)
    if not config_dir:
        return Configuration(data)
    for name in CONFIG_FILES:
        path = os.path.join(config_dir, f"{name}.json")
        if not os.path.isfile(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as handle:
                loaded = json.load(handle)
        except (OSError, ValueError) as exc:
            raise ConfigError(
                f"Le fichier de configuration \"{name}.json\" n'a pas pu être lu. "
                "Vérifiez qu'il s'agit d'un fichier JSON valide.",
                technical=f"{type(exc).__name__}: {exc}",
            ) from exc
        if not isinstance(loaded, dict):
            raise ConfigError(
                f"Le fichier de configuration \"{name}.json\" doit contenir un objet.",
                technical=f"config {name} is {type(loaded).__name__}",
            )
        data[name] = _deep_merge(data.get(name, {}), loaded)
    return Configuration(data)


def write_configuration(config_dir: str, section: str, data: Dict[str, Any]) -> str:
    """Ecrit une section de configuration, et rend le chemin du fichier.

    L'ecriture passe par un fichier temporaire du meme dossier, renomme
    ensuite : une interruption en cours d'ecriture laisserait sinon une
    configuration tronquee, que le chargement suivant refuserait.
    """
    if section not in CONFIG_FILES:
        raise ConfigError(
            f"La section de configuration \"{section}\" n'existe pas.",
            technical=f"unknown config section: {section}",
        )
    try:
        os.makedirs(config_dir, exist_ok=True)
        path = os.path.join(config_dir, f"{section}.json")
        temporary = path + ".tmp"
        with open(temporary, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temporary, path)
    except OSError as exc:
        raise ConfigError(
            f"Les paramètres n'ont pas pu être enregistrés dans "
            f"\"{config_dir}\". Vérifiez que le dossier est accessible en "
            "écriture, ou choisissez-en un autre.",
            technical=f"{type(exc).__name__}: {exc}",
        ) from exc
    return path


def write_default_configuration(config_dir: str) -> None:
    """Materialise les defauts sur disque, pour edition par l'utilisateur."""
    os.makedirs(config_dir, exist_ok=True)
    for name in CONFIG_FILES:
        path = os.path.join(config_dir, f"{name}.json")
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(DEFAULTS[name], handle, ensure_ascii=False, indent=2)
            handle.write("\n")
