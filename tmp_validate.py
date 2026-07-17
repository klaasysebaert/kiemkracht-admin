import time, subprocess, tempfile, uno
from com.sun.star.beans import PropertyValue

SOFFICE = r"C:\Program Files\LibreOffice\program\soffice.exe"
PORT = "2107"
BASE = r"C:\Users\klaas\projects\kiemkracht-admin"
PATHS = [BASE + r"\macro-kiemkracht-Module1",
         BASE + r"\macro-kiemkracht-Module2",
         BASE + r"\macro-kiemkracht-Module3",
         BASE + r"\macro-kiemkracht-Module4",
         BASE + r"\macro-kiemkracht-Module5"]

def boot(profile):
    args = [SOFFICE, "--headless", "--norestore", "--invisible", "--nologo",
            "--nofirststartwizard",
            "-env:UserInstallation=file:///" + profile.replace("\\", "/"),
            "--accept=socket,host=localhost,port=%s;urp;" % PORT]
    return subprocess.Popen(args)

def connect():
    lc = uno.getComponentContext()
    r = lc.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", lc)
    last = None
    for _ in range(60):
        try:
            return r.resolve("uno:socket,host=localhost,port=%s;urp;StarOffice.ComponentContext" % PORT)
        except Exception as e:
            last = e; time.sleep(1)
    raise RuntimeError(last)

def run(label, m1code, probe_mod, probe_fn, probe_args):
    profile = tempfile.mkdtemp(prefix="lo_v_")
    proc = boot(profile)
    try:
        ctx = connect()
        smgr = ctx.ServiceManager
        # macrobeveiliging op laag, anders draait/compileert de doc-macro niet
        from com.sun.star.beans import NamedValue
        cp = smgr.createInstanceWithContext("com.sun.star.configuration.ConfigurationProvider", ctx)
        upd = cp.createInstanceWithArguments(
            "com.sun.star.configuration.ConfigurationUpdateAccess",
            (NamedValue("nodepath", "/org.openoffice.Office.Common/Security/Scripting"),))
        upd.setPropertyValue("MacroSecurityLevel", 0)
        upd.commitChanges()
        p = PropertyValue(); p.Name = "Hidden"; p.Value = True
        desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
        doc = desktop.loadComponentFromURL("private:factory/scalc", "_blank", 0, (p,))
        libs = doc.BasicLibraries
        if libs.hasByName("CT"): libs.removeLibrary("CT")
        libs.createLibrary("CT"); libs.loadLibrary("CT")
        lib = libs.getByName("CT")
        codes = {}
        with open(PATHS[0], encoding="utf-8") as f: codes["Module1"] = m1code if m1code else f.read()
        with open(PATHS[1], encoding="utf-8") as f: codes["Module2"] = f.read()
        with open(PATHS[2], encoding="utf-8") as f: codes["Module3"] = f.read()
        with open(PATHS[3], encoding="utf-8") as f: codes["Module4"] = f.read()
        with open(PATHS[4], encoding="utf-8") as f: codes["Module5"] = f.read()
        for n, c in codes.items(): lib.insertByName(n, c)
        sp = doc.getScriptProvider()
        url = "vnd.sun.star.script:CT.%s.%s?language=Basic&location=document" % (probe_mod, probe_fn)
        try:
            script = sp.getScript(url)
            res = script.invoke(probe_args, (), ())
            print("[%s] GEEN FOUT (res=%r)" % (label, res[0]))
        except Exception as e:
            print("[%s] FOUT -> %s: %s" % (label, type(e).__name__, getattr(e, "Message", str(e))))
        doc.close(False)
    finally:
        try: proc.terminate()
        except Exception: pass

# 1) controle: opzettelijke compileerfout (ongedefinieerde var met Option Explicit)
with open(PATHS[0], encoding="utf-8") as f:
    orig = f.read()
broken = orig.replace("Sub MaakWeekbestand()",
                      "Sub MaakWeekbestand()\n    zzz_ongedefinieerd = 1", 1)
run("MET opzettelijke fout", broken, "Module1", "KolomLetter", (5,))

# 2) de echte huidige Module1 (KolomLetter forceert compilatie van de hele module)
run("ECHTE Module1", None, "Module1", "KolomLetter", (5,))

# 3) Module5-probes: compilatie + runtime van de pure helpers
run("Module5 SamMaatIdx (verwacht 2)", None, "Module5", "SamMaatIdx", ("extra-groot",))
run("Module5 SamBase64 (verwacht bG86dGVzdA==)", None, "Module5", "SamBase64", ("lo:test",))
run("Module5 SamJsonTekst", None, "Module5", "SamJsonTekst", ('a"b\nc\\d',))
run("Module5 SamJsNum (verwacht 0.9)", None, "Module5", "SamJsNum", (0.9,))
run("Module5 SamJsNum (verwacht -0.05)", None, "Module5", "SamJsNum", (-0.05,))
