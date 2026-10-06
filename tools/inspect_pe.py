#!/usr/bin/env python3
"""Lecture d'un executable Windows, pour la revue de securite.

    python3 tools/inspect_pe.py "dist/HR Analytics.exe"

Ce qu'il dit : les drapeaux de durcissement (ASLR, DEP, Control Flow
Guard), la presence d'un bloc de version, la table d'import complete, les
sections et leur entropie, la surcharge, et la signature Authenticode.

Il existe parce qu'une equipe de securite demande ces elements et qu'il
vaut mieux les produire que les promettre. Aucune bibliotheque tierce :
le format PE se lit avec « struct », et un auditeur peut relire ce
fichier en entier.
"""
import math, struct, sys

CARACTERISTIQUES = {
    0x0020: "HIGH_ENTROPY_VA",   # ASLR sur 64 bits
    0x0040: "DYNAMICBASE",       # ASLR
    0x0080: "FORCE_INTEGRITY",
    0x0100: "NX_COMPAT",         # DEP
    0x0200: "NO_ISOLATION",
    0x0400: "NO_SEH",
    0x0800: "NO_BIND",
    0x1000: "APPCONTAINER",
    0x2000: "WDM_DRIVER",
    0x4000: "GUARD_CF",          # Control Flow Guard
    0x8000: "TERMINAL_SERVER_AWARE",
}

def entropie(donnees):
    if not donnees:
        return 0.0
    compte = [0] * 256
    for octet in donnees:
        compte[octet] += 1
    n = len(donnees)
    return -sum((c / n) * math.log2(c / n) for c in compte if c)

class PE:
    def __init__(self, chemin):
        self.chemin = chemin
        with open(chemin, "rb") as f:
            self.brut = f.read()
        d = self.brut
        assert d[:2] == b"MZ", "pas un PE"
        self.pe = struct.unpack_from("<I", d, 0x3C)[0]
        assert d[self.pe:self.pe + 4] == b"PE\0\0", "signature PE absente"
        coff = self.pe + 4
        (self.machine, self.nb_sections, self.horodatage, _ps, _ns,
         self.taille_opt, self.caracteristiques) = struct.unpack_from(
            "<HHIIIHH", d, coff)
        opt = coff + 20
        self.magic = struct.unpack_from("<H", d, opt)[0]
        self.pe32plus = self.magic == 0x20B
        base = opt + (112 if self.pe32plus else 96)
        self.dll_caracteristiques = struct.unpack_from(
            "<H", d, opt + (70 if self.pe32plus else 70))[0]
        self.subsystem = struct.unpack_from("<H", d, opt + 68)[0]
        nb_rep = struct.unpack_from("<I", d, opt + (108 if self.pe32plus else 92))[0]
        self.repertoires = [struct.unpack_from("<II", d, base + 8 * i)
                            for i in range(nb_rep)]
        self.sections = []
        s0 = opt + self.taille_opt
        for i in range(self.nb_sections):
            o = s0 + 40 * i
            nom = d[o:o + 8].rstrip(b"\0").decode("latin-1")
            vtaille, vadr, rtaille, radr = struct.unpack_from("<IIII", d, o + 8)
            flags = struct.unpack_from("<I", d, o + 36)[0]
            self.sections.append(dict(nom=nom, vadr=vadr, vtaille=vtaille,
                                      radr=radr, rtaille=rtaille, flags=flags))

    def drapeaux(self):
        return [n for bit, n in sorted(CARACTERISTIQUES.items())
                if self.dll_caracteristiques & bit]

    def _decalage(self, rva):
        for s in self.sections:
            if s["vadr"] <= rva < s["vadr"] + max(s["vtaille"], s["rtaille"]):
                return s["radr"] + (rva - s["vadr"])
        return None

    def imports(self):
        if len(self.repertoires) < 2:
            return {}
        rva, taille = self.repertoires[1]
        if not rva:
            return {}
        o = self._decalage(rva)
        resultat = {}
        while True:
            champs = struct.unpack_from("<IIIII", self.brut, o)
            if not any(champs):
                break
            nom_rva = champs[3]
            no = self._decalage(nom_rva)
            fin = self.brut.index(b"\0", no)
            dll = self.brut[no:fin].decode("latin-1")
            fonctions = []
            thunk = self._decalage(champs[4] or champs[0])
            pas = 8 if self.pe32plus else 4
            fmt = "<Q" if self.pe32plus else "<I"
            while thunk:
                v = struct.unpack_from(fmt, self.brut, thunk)[0]
                if not v:
                    break
                ordinal = v & (1 << (63 if self.pe32plus else 31))
                if ordinal:
                    fonctions.append(f"#{v & 0xFFFF}")
                else:
                    fo = self._decalage(v & 0x7FFFFFFF)
                    if fo:
                        f2 = self.brut.index(b"\0", fo + 2)
                        fonctions.append(self.brut[fo + 2:f2].decode("latin-1"))
                thunk += pas
            resultat[dll] = fonctions
            o += 20
        return resultat

    def a_version_info(self):
        return b"VS_VERSION_INFO" in self.brut or b"V\0S\0_\0V\0E\0R" in self.brut

    def signature(self):
        if len(self.repertoires) < 5:
            return None
        adr, taille = self.repertoires[4]
        return (adr, taille) if taille else None

    def surcharge(self):
        """Octets situes apres la derniere section : la charge, et la
        signature. C'est ce qu'un antivirus appelle « overlay »."""
        fin = max((s["radr"] + s["rtaille"]) for s in self.sections)
        return fin, len(self.brut) - fin


def rapport(chemin: str) -> str:
    """Tout ce qu'une revue demande sur un executable, en un passage."""
    pe = PE(chemin)
    fin, surcharge = pe.surcharge()
    lignes = [f"{chemin}",
              f"  sous-systeme : " + {2: "GUI", 3: "console"}.get(pe.subsystem, str(pe.subsystem)),
              f"  durcissement : " + (", ".join(pe.drapeaux()) or "AUCUN"),
              f"  bloc version : " + ("present" if pe.a_version_info() else "ABSENT"),
              f"  signature    : " + ("presente" if pe.signature() else "aucune"),
              f"  surcharge    : {surcharge // 1024} Ko",
              "  sections :"]
    for s in pe.sections:
        bloc = pe.brut[s["radr"]:s["radr"] + min(s["rtaille"], 200000)]
        lignes.append(f"     {s['nom']:10} {s['rtaille'] // 1024:6} Ko"
                      f"   entropie {entropie(bloc):.2f}")
    lignes.append("  imports :")
    for dll, fonctions in sorted(pe.imports().items()):
        lignes.append(f"     {dll} ({len(fonctions)})")
        for nom in sorted(fonctions):
            lignes.append(f"        {nom}")
    return "\n".join(lignes)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("usage : inspect_pe.py <executable.exe> [...]")
    for chemin in sys.argv[1:]:
        print(rapport(chemin))
        print()
