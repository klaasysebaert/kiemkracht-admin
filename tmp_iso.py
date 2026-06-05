import time, subprocess, tempfile, uno
from com.sun.star.beans import PropertyValue

SOFFICE = r"C:\Program Files\LibreOffice\program\soffice.exe"
PORT = "2113"
BASE = r"C:\Users\klaas\projects\kiemkracht-admin"
SRC = {
    "Module1": BASE + r"\macro-kiemkracht-Module1",
    "Module2": BASE + r"\macro-kiemkracht-Module2",
    "Module3": BASE + r"\macro-kiemkracht-Module3",
}

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

def main():
    profile = tempfile.mkdtemp(prefix="lo_iso_")
    proc = boot(profile)
    src = {k: open(v, encoding="utf-8").read() for k, v in SRC.items()}
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
        sp = doc.getScriptProvider()

        combos = [
            ("M1",      ["Module1"]),
            ("M1+M2",   ["Module1", "Module2"]),
            ("M1+M3",   ["Module1", "Module3"]),
            ("M1+M2+M3",["Module1", "Module2", "Module3"]),
        ]
        for label, mods in combos:
            name = "CT_" + label.replace("+", "_")
            if libs.hasByName(name): libs.removeLibrary(name)
            libs.createLibrary(name); libs.loadLibrary(name)
            lib = libs.getByName(name)
            for m in mods:
                lib.insertByName(m, src[m])
            url = "vnd.sun.star.script:%s.Module1.KolomLetter?language=Basic&location=document" % name
            try:
                res = sp.getScript(url).invoke((5,), (), ())[0]
                print("[%-9s] KolomLetter(5) = %r  %s" % (label, res, "OK" if res == "F" else "<<< BREUK"))
            except Exception as e:
                print("[%-9s] FOUT -> %s: %s" % (label, type(e).__name__, getattr(e, "Message", str(e))))
        doc.close(False)
    finally:
        try: proc.terminate()
        except Exception: pass

main()
