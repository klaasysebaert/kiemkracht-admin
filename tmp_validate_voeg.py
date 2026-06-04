import time, subprocess, tempfile, uno
from com.sun.star.beans import PropertyValue

SOFFICE = r"C:\Program Files\LibreOffice\program\soffice.exe"
PORT = "2111"
BASE = r"C:\Users\klaas\projects\kiemkracht-admin"
PATHS = [BASE + r"\macro-kiemkracht-Module1",
         BASE + r"\macro-kiemkracht-Module2",
         BASE + r"\macro-kiemkracht-Module3"]

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

def run(label, m1code):
    profile = tempfile.mkdtemp(prefix="lo_vv_")
    proc = boot(profile)
    try:
        ctx = connect()
        smgr = ctx.ServiceManager
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
        for n, c in codes.items(): lib.insertByName(n, c)
        sp = doc.getScriptProvider()
        url = "vnd.sun.star.script:CT.Module1.KolomLetter?language=Basic&location=document"
        try:
            res = sp.getScript(url).invoke((5,), (), ())
            print("[%s] GEEN FOUT (res=%r)" % (label, res[0]))
        except Exception as e:
            print("[%s] FOUT -> %s: %s" % (label, type(e).__name__, getattr(e, "Message", str(e))))
        doc.close(False)
    finally:
        try: proc.terminate()
        except Exception: pass

with open(PATHS[0], encoding="utf-8") as f:
    orig = f.read()

# Injecteer een STRUCTURELE syntaxfout in VoegLosseGroenteToe: een 'If True Then'
# zonder bijbehorende End If. Als module-load de hele module tokeniseert, moet
# dit een compile/parse-fout geven (ook al roepen we KolomLetter aan).
assert "Sub VoegLosseGroenteToe()" in orig, "Sub niet gevonden"
broken = orig.replace("Sub VoegLosseGroenteToe()",
                      "Sub VoegLosseGroenteToe()\n    If True Then", 1)
run("syntaxfout in VoegLosseGroenteToe", broken)
run("ECHTE Module1", None)
