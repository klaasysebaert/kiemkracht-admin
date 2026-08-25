"""Compile-check van de Kiemkracht-macro's in PRODUCTIE-scope.

Waarom dit bestaat naast tmp_validate.py
----------------------------------------
tmp_validate.py duwt de modules in een tijdelijke DOC-library van een vers Calc-
document. Die aanpak geeft sinds 2026-07-06 vals-negatieve resultaten (res='' bij
code die in productie prima draait) en — erger — ze bleek op 2026-07-20 ook een
ECHTE structuurfout niet te melden. Ze discrimineert dus niet en bewijst niets.

Deze probe laadt in plaats daarvan de gesynchroniseerde GEBRUIKERSBIBLIOTHEEK
(dezelfde scope waarin de macro's echt draaien: GlobalScope / location=application)
in een vers LibreOffice met een tijdelijk profiel. Aangetoond op 2026-08-04:

  - echte library      -> KolomLetter(5) = 'F'   (alles compileert)
  - met 1 kapotte If   -> KolomLetter(5) = None  (fout gemeld)

Dus: een 'F' hier is wél bewijs dat de library compileert.

Gebruik (met de python VAN LibreOffice, die heeft de uno-module):
    & "C:\\Program Files\\LibreOffice\\program\\python.exe" validate-macro.py
    & "C:\\Program Files\\LibreOffice\\program\\python.exe" validate-macro.py --zelftest

Draai dit NA sync-macro.ps1 — de probe test de gesynchroniseerde bibliotheek in
%APPDATA%, niet de bronbestanden in deze repo.

Wat het NIET vangt: echt niet-gedeclareerde variabelen (die zijn onder Option
Explicit lui per procedure) en alle logische fouten. Een echte macro-run in
LibreOffice blijft de laatste stap.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import time

import uno

SOFFICE = r"C:\Program Files\LibreOffice\program\soffice.exe"
ECHT_BASIC = r"C:\Users\klaas\AppData\Roaming\LibreOffice\4\user\basic"

# (module, functie, argumenten, verwachte uitkomst) — pure helpers zonder UI/DB.
# Eén aanroep per module volstaat: een structuurfout ergens in dat module (of in
# een module dat het gebruikt) breekt de compilatie ervan.
PROBES = [
    ("Module1", "KolomLetter", (5,), "F"),
    ("Module1", "KolomLetter", (43,), "AR"),
    ("Module2", "Base64Encode", ("lo:test",), "bG86dGVzdA=="),
    ("Module4", "ProviderTip", ("onbekend.be",), ""),
    ("Module5", "SamMaatIdx", ("extra-groot",), 2),
    ("Module5", "SamBase64", ("lo:test",), "bG86dGVzdA=="),
    ("Module5", "SamBestandsnaam",
     ("file:///C:/x/2026_week_35/week_35_2026_definitief.ods",),
     "week_35_2026_definitief.ods"),
    ("Module6", "KlasLaatsteStatus", (), ""),
    # Omgevingsbepaling: welke database een macro raakt hangt hiervan af, dus
    # de naamregel zelf ook echt aftoetsen en niet enkel laten compileren.
    ("Module1", "OmgevingUitNaam",
     ("file:///C:/x/2026_week_34/samenstelling_34_2026.ods",), "prod"),
    ("Module1", "OmgevingUitNaam",
     ("file:///C:/x/2026_week_34/samenstelling_34_2026-dev.ods",), "dev"),
    ("Module1", "OmgevingUitNaam",
     ("file:///C:/x/kiemkracht-data.ods",), "prod"),
    ("Module1", "OmgevingUitNaam",
     ("file:///C:/x/kiemkracht-data-dev.ods",), "dev"),
]


def boot(profiel, poort):
    args = [SOFFICE, "--headless", "--norestore", "--invisible", "--nologo",
            "--nofirststartwizard",
            "-env:UserInstallation=file:///" + profiel.replace("\\", "/"),
            "--accept=socket,host=localhost,port=%s;urp;" % poort]
    return subprocess.Popen(args)


def verbind(poort):
    lc = uno.getComponentContext()
    resolver = lc.ServiceManager.createInstanceWithContext(
        "com.sun.star.bridge.UnoUrlResolver", lc)
    laatste = None
    for _ in range(60):
        try:
            return resolver.resolve(
                "uno:socket,host=localhost,port=%s;urp;StarOffice.ComponentContext" % poort)
        except Exception as e:          # nog niet klaar met opstarten
            laatste = e
            time.sleep(1)
    raise RuntimeError("geen verbinding met soffice: %s" % laatste)


def keur(basic_map, poort, label):
    """Boot LO met basic_map als gebruikersbibliotheek en draai de probes.
    Geeft True als alle probes de verwachte waarde teruggeven."""
    profiel = tempfile.mkdtemp(prefix="lo_val_")
    proces = None
    try:
        # Fase 1: LO het profiel laten aanmaken. Kopieer je de basic-map vóór de
        # eerste start, dan overschrijft die start script.xlc en is de
        # Kiemkracht-bibliotheek niet geregistreerd ("script could not be found").
        eerste = boot(profiel, poort)
        verbind(poort)
        eerste.terminate()
        time.sleep(4)

        doel = os.path.join(profiel, "user", "basic")
        shutil.rmtree(doel, ignore_errors=True)
        shutil.copytree(basic_map, doel)

        # Fase 2: opnieuw booten, nu mét de te keuren bibliotheek.
        proces = boot(profiel, poort)
        ctx = verbind(poort)
        smgr = ctx.ServiceManager
        smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
        provider = smgr.createInstanceWithContext(
            "com.sun.star.script.provider.MasterScriptProviderFactory", ctx
        ).createScriptProvider("")

        alles_ok = True
        for module, functie, args, verwacht in PROBES:
            url = ("vnd.sun.star.script:Kiemkracht.%s.%s?language=Basic&location=application"
                   % (module, functie))
            try:
                res = provider.getScript(url).invoke(args, (), ())[0]
                ok = (res == verwacht)
                print("  %s %s.%s%r -> %r (verwacht %r)"
                      % ("OK" if ok else "!!", module, functie, args, res, verwacht))
            except Exception as e:
                ok = False
                print("  !! %s.%s -> %s: %s"
                      % (module, functie, type(e).__name__, getattr(e, "Message", str(e))))
            alles_ok = alles_ok and ok
        print("[%s] %s" % (label, "COMPILEERT" if alles_ok else "FOUT"))
        return alles_ok
    finally:
        if proces is not None:
            try:
                proces.terminate()
            except Exception:
                pass
        time.sleep(2)
        shutil.rmtree(profiel, ignore_errors=True)


def maak_kapotte_kopie(doel):
    """Kopie van de bibliotheek met een If zonder End If in MaakWeekbestand."""
    shutil.rmtree(doel, ignore_errors=True)
    shutil.copytree(ECHT_BASIC, doel)
    pad = os.path.join(doel, "Kiemkracht", "Module1.xba")
    with open(pad, encoding="utf-8") as f:
        xba = f.read()
    anker = "Sub MaakWeekbestand()"
    if xba.count(anker) != 1:
        raise RuntimeError("anker %r komt %d keer voor" % (anker, xba.count(anker)))
    xba = xba.replace(anker, anker + "\n    If 1 = 1 Then   ' OPZETTELIJKE FOUT", 1)
    with open(pad, "w", encoding="utf-8") as f:
        f.write(xba)


if __name__ == "__main__":
    print("Echte gebruikersbibliotheek:", ECHT_BASIC)
    goed = keur(ECHT_BASIC, "2119", "echte library")

    if "--zelftest" in sys.argv:
        # Controleproef: dezelfde bibliotheek mét een structuurfout MOET falen.
        # Zonder deze stap weet je niet of een 'COMPILEERT' iets betekent.
        kapot = os.path.join(tempfile.gettempdir(), "kiemkracht_basic_kapot")
        print("\nControleproef (opzettelijke fout, hoort te FALEN):")
        maak_kapotte_kopie(kapot)
        try:
            slecht = keur(kapot, "2120", "opzettelijk kapot")
        finally:
            shutil.rmtree(kapot, ignore_errors=True)
        if slecht:
            print("\n!! De probe discrimineert NIET (kapotte code werd goedgekeurd) "
                  "- vertrouw het resultaat hierboven niet.")
            sys.exit(2)
        print("\nControleproef in orde: de probe meldt echte fouten.")

    sys.exit(0 if goed else 1)
