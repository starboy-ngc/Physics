/*
 * HR Analytics — lanceur Windows.
 *
 * Son seul travail : demarrer l'interpreteur Python prive qui dort dans le
 * sous-dossier « runtime », et lui demander d'ouvrir l'outil. L'utilisateur
 * double-clique un fichier ; il n'installe rien, ne tape rien, et n'a pas
 * besoin de savoir que Python existe.
 *
 * Ce que ce lanceur ne fait PAS, et pourquoi :
 *
 *   Rien n'est extrait nulle part. Les outils qui replient tout dans un
 *   .exe unique se decompressent au demarrage dans %TEMP% et s'executent
 *   depuis la — le comportement meme qu'une protection de poste
 *   sanctionne, et la cause la plus frequente des blocages en entreprise.
 *   Ici tout est deja sur le disque, lisible, a cote du lanceur.
 *
 *   Aucun interpreteur du poste n'est cherche. Ni le PATH, ni le registre,
 *   ni une variable d'environnement : l'interpreteur employe est celui du
 *   dossier, et lui seul. Deux postes font donc le meme calcul, quoi qu'ils
 *   aient installe par ailleurs.
 *
 *   Aucun chemin n'est ecrit en dur. Tout se deduit de l'emplacement du
 *   lanceur. Le dossier se deplace, se copie sur une cle, se pose sur un
 *   partage reseau : il fonctionne sans etre reparametre.
 *
 * Une version precedente chargeait python312.dll dans son propre processus
 * et appelait Py_Main, pour n'avoir aucun processus fils. Elle ne demarrait
 * pas : ce lanceur est compile avec mingw, python312.dll avec le
 * compilateur de Microsoft, et les deux embarquent chacun leur
 * bibliotheque C. Chargee en DLL, celle de Python n'a pas de descripteurs
 * d'entree et de sortie standard, et l'initialisation s'arrete sur
 * « can't initialize sys standard streams ». Poser les poignees Windows
 * n'y change rien : elles ne sont pas ce que la bibliotheque C regarde.
 *
 * On demarre donc pythonw.exe — celui du dossier — comme le fait toute
 * application Python sous Windows. L'arbre des processus montre
 * « HR Analytics.exe » puis « pythonw.exe » : c'est lisible, et plus honnete
 * qu'un interpreteur cache dans le lanceur.
 *
 * Compilation (chaine croisee, depuis Linux) :
 *   x86_64-w64-mingw32-gcc -O2 -municode -mwindows lanceur.c \
 *       -o "HR Analytics.exe"
 */

#include <windows.h>

/* Le sous-dossier de l'interpreteur, et l'executable sans console qui s'y
 * trouve. Deux lignes a changer le jour ou l'outil suivra une version plus
 * recente de Python. */
#define RUNTIME_DIR L"\\runtime"
#define RUNTIME_EXE L"\\runtime\\pythonw.exe"

/* Ce qu'on lui demande d'executer. « -I » : mode isole — aucun paquet
 * installe ailleurs sur le poste, aucune variable d'environnement, aucun
 * repertoire de l'utilisateur ne peut s'inviter dans l'analyse. */
#define COMMANDE L"\" -I -m hr_analytics"

static void erreur(const wchar_t *message)
{
    MessageBoxW(NULL, message, L"HR Analytics", MB_ICONERROR | MB_OK);
}

int WINAPI wWinMain(HINSTANCE instance, HINSTANCE precedente,
                    PWSTR arguments, int affichage)
{
    (void)instance; (void)precedente; (void)arguments; (void)affichage;

    /* Ou suis-je ? Tout le reste en decoule. */
    wchar_t dossier[MAX_PATH];
    DWORD taille = GetModuleFileNameW(NULL, dossier, MAX_PATH);
    if (taille == 0 || taille >= MAX_PATH) {
        erreur(L"Le lanceur n'a pas pu determiner son propre emplacement.\n\n"
               L"Placez le dossier HR Analytics dans un chemin plus court, "
               L"par exemple C:\\HR Analytics.");
        return 1;
    }
    /* Retirer le nom du fichier : il reste le dossier. */
    for (DWORD rang = taille; rang > 0; rang--) {
        if (dossier[rang - 1] == L'\\') { dossier[rang - 1] = L'\0'; break; }
    }

    wchar_t interpreteur[MAX_PATH];
    lstrcpynW(interpreteur, dossier, MAX_PATH);
    lstrcatW(interpreteur, RUNTIME_EXE);
    if (GetFileAttributesW(interpreteur) == INVALID_FILE_ATTRIBUTES) {
        erreur(L"Le moteur de HR Analytics est introuvable.\n\n"
               L"Le sous-dossier « runtime » doit rester a cote du lanceur. "
               L"Si vous avez deplace le programme, recopiez le dossier "
               L"HR Analytics en entier.");
        return 2;
    }

    /* La ligne de commande, guillemets compris : le chemin peut contenir
     * des espaces, et « C:\\Mes documents\\HR Analytics » est le cas normal
     * et non l'exception. */
    wchar_t ligne[MAX_PATH + 64];
    lstrcpynW(ligne, L"\"", 2);
    lstrcatW(ligne, interpreteur);
    lstrcatW(ligne, COMMANDE);

    STARTUPINFOW demarrage;
    PROCESS_INFORMATION processus;
    ZeroMemory(&demarrage, sizeof(demarrage));
    demarrage.cb = sizeof(demarrage);
    ZeroMemory(&processus, sizeof(processus));

    /* Le dossier de l'outil est le repertoire de travail : c'est la que
     * l'outil ira chercher « config », et la que l'utilisateur s'attend a
     * enregistrer ses documents.
     *
     * CREATE_NO_WINDOW : aucune fenetre de console derriere l'outil, meme
     * une fraction de seconde. */
    if (!CreateProcessW(interpreteur, ligne, NULL, NULL, FALSE,
                        CREATE_NO_WINDOW, NULL, dossier,
                        &demarrage, &processus)) {
        erreur(L"HR Analytics n'a pas pu demarrer.\n\n"
               L"Verifiez que le dossier n'est pas en lecture seule et que "
               L"votre antivirus n'a pas mis le programme en quarantaine.");
        return 3;
    }

    /* On attend l'outil au lieu de rendre la main tout de suite. Le lanceur
     * reste ainsi le programme que l'utilisateur voit dans sa barre des
     * taches, et un demarrage qui echoue peut encore etre explique — rendre
     * la main aussitot aurait fait disparaitre l'icone sans un mot. */
    WaitForSingleObject(processus.hProcess, INFINITE);
    DWORD code = 0;
    GetExitCodeProcess(processus.hProcess, &code);
    CloseHandle(processus.hProcess);
    CloseHandle(processus.hThread);

    /* Un code non nul avant que la fenetre ait eu le temps de s'ouvrir est
     * presque toujours un dossier incomplet. Le dire vaut mieux que de
     * disparaitre. */
    if (code != 0) {
        erreur(L"HR Analytics s'est arrete sur une erreur.\n\n"
               L"Si le probleme se repete, recopiez le dossier HR Analytics "
               L"en entier depuis sa source.");
    }
    return (int)code;
}
