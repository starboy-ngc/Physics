/*
 * HR Analytics — lanceur a fichier unique.
 *
 * Un seul .exe. Il porte l'outil, l'interpreteur Python et Tcl/Tk, replies
 * derriere son propre code sous forme d'archive. Au premier lancement il
 * les depose dans le profil de l'utilisateur, puis demarre l'outil. Aux
 * lancements suivants il trouve le depot deja en place et demarre
 * directement.
 *
 * CE QU'IL FAUT SAVOIR DE CE CHOIX
 *
 * Un fichier unique coute quelque chose, et autant le dire ici plutot que
 * de le decouvrir en production :
 *
 *   - Un executable qui ecrit d'autres executables sur le disque puis les
 *     lance est exactement le motif qu'une protection de poste surveille.
 *     Le dossier livre a cote, lui, ne fait rien de tel. C'est le prix du
 *     fichier unique, et aucune astuce ne le supprime.
 *
 *   - Le depot va dans %LOCALAPPDATA%, et non dans %TEMP%. C'est deja
 *     beaucoup mieux : %TEMP% est efface, surveille de pres, et souvent
 *     interdit d'execution par strategie de groupe. LOCALAPPDATA est
 *     l'endroit prevu pour cela, et l'extraction n'a lieu qu'une fois.
 *
 *   - Le depot porte le numero de version dans son nom. Une version plus
 *     recente s'installe a cote de l'ancienne au lieu de l'ecraser a
 *     moitie, et la configuration, elle, reste au-dessus : elle survit aux
 *     mises a jour.
 *
 * L'archive est un CAB, et c'est Windows lui-meme qui la deplie —
 * SetupIterateCabinetW, presente depuis toujours. Aucune bibliotheque de
 * decompression n'est embarquee : il n'y a donc rien a auditer de ce
 * cote-la, et rien qui puisse etre vulnerable.
 *
 * Compilation (chaine croisee, depuis Linux) :
 *   x86_64-w64-mingw32-windres icone.rc -o icone.o
 *   x86_64-w64-mingw32-gcc -O2 -municode -mwindows \
 *       lanceur-unique.c icone.o -lsetupapi -o "HR Analytics.exe"
 * puis l'archive est ajoutee a la suite du fichier par build_windows.py.
 */

#include <windows.h>
#include <setupapi.h>
#include <shlobj.h>

/* Marque de fin, posee juste avant la taille de l'archive. Elle permet de
 * reconnaitre un executable qui porte sa charge d'un executable nu. */
#define MARQUE "HRANALYT"
#define MARQUE_TAILLE 8
#define PIED_TAILLE (MARQUE_TAILLE + 8 + 4)

/* Fin de fichier balayee a la recherche de la marque. Une signature de
 * code pese quelques kilo-octets ; un mega-octet est large. */
#define FENETRE_RECHERCHE (1024 * 1024)

#define NOM_PRODUIT L"HR Analytics"
#define RUNTIME_EXE L"\\runtime\\pythonw.exe"
#define COMMANDE L"\" -I -m hr_analytics"

static void erreur(const wchar_t *message)
{
    MessageBoxW(NULL, message, NOM_PRODUIT, MB_ICONERROR | MB_OK);
}

/* ------------------------------------------------------------- extraction */

/* Cree un dossier et tous ses parents. Declare ici, defini plus bas. */
static BOOL creer_dossier(const wchar_t *chemin);

/* Cree l'arborescence qui portera un fichier. */
static void creer_parent(const wchar_t *fichier)
{
    wchar_t dossier[MAX_PATH];
    lstrcpynW(dossier, fichier, MAX_PATH);
    for (int rang = lstrlenW(dossier); rang > 0; rang--) {
        if (dossier[rang - 1] == L'\\') {
            dossier[rang - 1] = L'\0';
            creer_dossier(dossier);
            return;
        }
    }
}

/* Rappel de SetupIterateCabinetW. Windows annonce chaque fichier de
 * l'archive ; on repond ou l'ecrire, et il l'ecrit. */
static UINT CALLBACK deplier(PVOID contexte, UINT notification,
                             UINT_PTR param1, UINT_PTR param2)
{
    (void)param2;
    const wchar_t *destination = (const wchar_t *)contexte;
    if (notification == SPFILENOTIFY_FILEINCABINET) {
        FILE_IN_CABINET_INFO_W *fichier = (FILE_IN_CABINET_INFO_W *)param1;
        wchar_t cible[MAX_PATH];
        lstrcpynW(cible, destination, MAX_PATH);
        lstrcatW(cible, L"\\");
        lstrcatW(cible, fichier->NameInCabinet);
        /* Les separateurs d'une archive peuvent etre des barres obliques
         * selon l'outil qui l'a faite ; Windows veut des antislashs pour
         * creer les dossiers. */
        for (wchar_t *lettre = cible; *lettre; lettre++) {
            if (*lettre == L'/') {
                *lettre = L'\\';
            }
        }
        /* Windows deplie les fichiers mais ne cree pas les dossiers qui
         * les portent : sans cette ligne, tout ce qui n'est pas a la
         * racine de l'archive est silencieusement perdu. */
        creer_parent(cible);
        lstrcpynW(fichier->FullTargetName, cible, MAX_PATH);
        return FILEOP_DOIT;
    }
    if (notification == SPFILENOTIFY_NEEDNEWCABINET) {
        /* Une archive en plusieurs morceaux : il n'y en a qu'un. */
        return ERROR_NOT_ENOUGH_MEMORY;
    }
    return NO_ERROR;
}

/* SHCreateDirectoryExW cree un dossier et tous ses parents. Il fait
 * partie de Windows depuis Windows 2000. */
static BOOL creer_dossier(const wchar_t *chemin)
{
    int code = SHCreateDirectoryExW(NULL, chemin, NULL);
    return code == ERROR_SUCCESS || code == ERROR_ALREADY_EXISTS
           || code == ERROR_FILE_EXISTS;
}

/* Ecrit la charge utile de l'executable dans un fichier .cab temporaire,
 * a cote du depot — jamais dans %TEMP%, dont l'execution est parfois
 * interdite et qui est le premier endroit qu'une protection surveille. */
static BOOL ecrire_archive(const wchar_t *moi, LONGLONG debut,
                           LONGLONG taille, const wchar_t *cible)
{
    HANDLE source = CreateFileW(moi, GENERIC_READ, FILE_SHARE_READ, NULL,
                                OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    if (source == INVALID_HANDLE_VALUE) {
        return FALSE;
    }
    HANDLE sortie = CreateFileW(cible, GENERIC_WRITE, 0, NULL, CREATE_ALWAYS,
                                FILE_ATTRIBUTE_NORMAL, NULL);
    if (sortie == INVALID_HANDLE_VALUE) {
        CloseHandle(source);
        return FALSE;
    }
    LARGE_INTEGER position;
    position.QuadPart = debut;
    SetFilePointerEx(source, position, NULL, FILE_BEGIN);

    BOOL bon = TRUE;
    char tampon[65536];
    LONGLONG reste = taille;
    while (reste > 0) {
        DWORD a_lire = (DWORD)(reste < (LONGLONG)sizeof(tampon)
                               ? reste : (LONGLONG)sizeof(tampon));
        DWORD lus = 0, ecrits = 0;
        if (!ReadFile(source, tampon, a_lire, &lus, NULL) || lus == 0) {
            bon = FALSE;
            break;
        }
        if (!WriteFile(sortie, tampon, lus, &ecrits, NULL) || ecrits != lus) {
            bon = FALSE;
            break;
        }
        reste -= lus;
    }
    CloseHandle(sortie);
    CloseHandle(source);
    return bon;
}

/* --------------------------------------------------------------- lancement */

int WINAPI wWinMain(HINSTANCE instance, HINSTANCE precedente,
                    PWSTR arguments, int affichage)
{
    (void)instance; (void)precedente; (void)arguments; (void)affichage;

    wchar_t moi[MAX_PATH];
    DWORD taille_chemin = GetModuleFileNameW(NULL, moi, MAX_PATH);
    if (taille_chemin == 0 || taille_chemin >= MAX_PATH) {
        erreur(L"Le programme n'a pas pu determiner son propre "
               L"emplacement.\n\nPlacez-le dans un chemin plus court.");
        return 1;
    }

    /* Retrouver le pied : la marque, la taille de l'archive, son empreinte.
     *
     * Le pied n'est pas forcement le dernier octet du fichier. Signer un
     * executable Windows ajoute la signature a la suite de tout le reste :
     * elle se retrouve donc APRES la charge. Une premiere version lisait
     * les vingt derniers octets et refusait net tout executable signe —
     * ce qui s'est vu au premier essai de signature, et pas avant.
     *
     * On cherche donc la marque a rebours, dans la fin du fichier. Une
     * signature pese quelques kilo-octets ; un mega-octet de marge est
     * genereux et ne coute qu'une lecture. */
    HANDLE fichier = CreateFileW(moi, GENERIC_READ, FILE_SHARE_READ, NULL,
                                 OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    if (fichier == INVALID_HANDLE_VALUE) {
        erreur(L"Le programme n'a pas pu se relire lui-meme.\n\n"
               L"Verifiez que votre antivirus ne l'a pas mis en "
               L"quarantaine.");
        return 2;
    }
    LARGE_INTEGER poids;
    GetFileSizeEx(fichier, &poids);
    DWORD fenetre = (DWORD)(poids.QuadPart < (LONGLONG)FENETRE_RECHERCHE
                            ? poids.QuadPart : (LONGLONG)FENETRE_RECHERCHE);
    char *fin = (char *)HeapAlloc(GetProcessHeap(), 0, fenetre);
    if (fin == NULL) {
        CloseHandle(fichier);
        erreur(L"Memoire insuffisante pour demarrer.");
        return 2;
    }
    LARGE_INTEGER position;
    position.QuadPart = poids.QuadPart - fenetre;
    SetFilePointerEx(fichier, position, NULL, FILE_BEGIN);
    DWORD lus = 0;
    ReadFile(fichier, fin, fenetre, &lus, NULL);
    CloseHandle(fichier);

    LONGLONG taille_archive = 0;
    LONGLONG debut_archive = 0;
    unsigned int empreinte = 0;
    BOOL trouve = FALSE;
    for (LONGLONG rang = (LONGLONG)lus - PIED_TAILLE; rang >= 0; rang--) {
        if (memcmp(fin + rang, MARQUE, MARQUE_TAILLE) != 0) {
            continue;
        }
        LONGLONG annoncee = 0;
        memcpy(&annoncee, fin + rang + MARQUE_TAILLE, 8);
        /* Le pied commence a cette position dans le fichier entier. */
        LONGLONG pied_absolu = poids.QuadPart - lus + rang;
        LONGLONG depart = pied_absolu - annoncee;
        if (annoncee > 0 && depart > 0 && depart < pied_absolu) {
            memcpy(&empreinte, fin + rang + MARQUE_TAILLE + 8, 4);
            taille_archive = annoncee;
            debut_archive = depart;
            trouve = TRUE;
            break;
        }
    }
    HeapFree(GetProcessHeap(), 0, fin);
    if (!trouve) {
        erreur(L"Ce fichier ne porte pas HR Analytics : il a ete tronque ou "
               L"modifie.\n\nRecopiez-le depuis sa source.");
        return 3;
    }

    /* Le depot : %LOCALAPPDATA%\HR Analytics\, et dedans un dossier par
     * version. L'empreinte de l'archive sert de numero : deux versions
     * differentes ne peuvent pas se melanger, et la meme version ne se
     * reextrait jamais. */
    wchar_t base[MAX_PATH];
    if (!SUCCEEDED(SHGetFolderPathW(NULL, CSIDL_LOCAL_APPDATA, NULL, 0,
                                    base))) {
        erreur(L"Le dossier personnel de l'utilisateur est introuvable.");
        return 4;
    }
    lstrcatW(base, L"\\");
    lstrcatW(base, NOM_PRODUIT);
    if (!creer_dossier(base)) {
        erreur(L"HR Analytics n'a pas pu creer son dossier de travail.\n\n"
               L"Verifiez vos droits sur votre profil utilisateur.");
        return 4;
    }

    wchar_t depot[MAX_PATH];
    wchar_t numero[32];
    wsprintfW(numero, L"\\%08x", empreinte);
    lstrcpynW(depot, base, MAX_PATH);
    lstrcatW(depot, numero);

    wchar_t interpreteur[MAX_PATH];
    lstrcpynW(interpreteur, depot, MAX_PATH);
    lstrcatW(interpreteur, RUNTIME_EXE);

    if (GetFileAttributesW(interpreteur) == INVALID_FILE_ATTRIBUTES) {
        /* Premier lancement de cette version : on deplie. */
        if (!creer_dossier(depot)) {
            erreur(L"HR Analytics n'a pas pu creer son dossier de travail.");
            return 4;
        }
        wchar_t archive[MAX_PATH];
        lstrcpynW(archive, depot, MAX_PATH);
        lstrcatW(archive, L"\\paquet.cab");
        if (!ecrire_archive(moi, debut_archive, taille_archive, archive)) {
            erreur(L"HR Analytics n'a pas pu preparer son installation.\n\n"
                   L"Verifiez l'espace disque disponible sur votre profil.");
            return 5;
        }
        BOOL deplie = SetupIterateCabinetW(archive, 0, deplier, (PVOID)depot);
        DeleteFileW(archive);
        if (!deplie) {
            erreur(L"HR Analytics n'a pas pu se deplier.\n\n"
                   L"Verifiez l'espace disque, puis relancez. Si le "
                   L"probleme persiste, recopiez le fichier depuis sa "
                   L"source.");
            return 5;
        }
    }

    /* La configuration vit au-dessus des versions : elle survit aux mises
     * a jour. Au premier lancement, celle qui accompagne l'outil lui sert
     * de point de depart. */
    wchar_t config[MAX_PATH];
    lstrcpynW(config, base, MAX_PATH);
    lstrcatW(config, L"\\config");
    if (GetFileAttributesW(config) == INVALID_FILE_ATTRIBUTES) {
        wchar_t origine[MAX_PATH + 2];
        wchar_t cible[MAX_PATH + 2];
        ZeroMemory(origine, sizeof(origine));
        ZeroMemory(cible, sizeof(cible));
        lstrcpynW(origine, depot, MAX_PATH);
        lstrcatW(origine, L"\\config");
        lstrcpynW(cible, config, MAX_PATH);
        /* SHFileOperation veut des chaines terminees par deux zeros. */
        SHFILEOPSTRUCTW copie;
        ZeroMemory(&copie, sizeof(copie));
        copie.wFunc = FO_COPY;
        copie.pFrom = origine;
        copie.pTo = cible;
        copie.fFlags = FOF_NO_UI | FOF_NOCONFIRMMKDIR;
        SHFileOperationW(&copie);
    }

    wchar_t ligne[MAX_PATH + 64];
    lstrcpynW(ligne, L"\"", 2);
    lstrcatW(ligne, interpreteur);
    lstrcatW(ligne, COMMANDE);

    STARTUPINFOW demarrage;
    PROCESS_INFORMATION processus;
    ZeroMemory(&demarrage, sizeof(demarrage));
    demarrage.cb = sizeof(demarrage);
    ZeroMemory(&processus, sizeof(processus));

    /* Repertoire de travail : le dossier de configuration, au-dessus des
     * versions. C'est la que l'outil trouvera « config », et la que
     * l'utilisateur s'attend a enregistrer ses documents. */
    if (!CreateProcessW(interpreteur, ligne, NULL, NULL, FALSE,
                        CREATE_NO_WINDOW, NULL, base,
                        &demarrage, &processus)) {
        erreur(L"HR Analytics n'a pas pu demarrer.\n\n"
               L"Verifiez que votre antivirus n'a pas mis le programme en "
               L"quarantaine.");
        return 6;
    }
    WaitForSingleObject(processus.hProcess, INFINITE);
    DWORD code = 0;
    GetExitCodeProcess(processus.hProcess, &code);
    CloseHandle(processus.hProcess);
    CloseHandle(processus.hThread);
    if (code != 0) {
        erreur(L"HR Analytics s'est arrete sur une erreur.\n\n"
               L"Si le probleme se repete, supprimez le dossier "
               L"« HR Analytics » de votre profil utilisateur et relancez : "
               L"le programme se reinstallera.");
    }
    return (int)code;
}
