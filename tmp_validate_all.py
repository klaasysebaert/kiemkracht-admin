import time, subprocess, tempfile, uno
from com.sun.star.beans import PropertyValue

SOFFICE = r"C:\Program Files\LibreOffice\program\soffice.exe"
PORT = "2112"
BASE = r"C:\Users\klaas\projects\kiemkracht-admin"
PATHS = [BASE + r"\macro-kiemkracht-Module1",
         BASE + r"\macro-kiemkracht-Module2",
         BASE + r"\macro-kiemkracht-Module3"]

# (module, functie, args, verwachte waarde)  -- invoke forceert structurele compile
PROBES = [
    ("Module1", "KolomLetter",   (5,),            "F"),
    ("Module2", "FmtNum2",       (5.0,),          None),   # niet-None = OK
    ("Module3", "EenheidUitRij3", ("5,00 / kg",), "kg"),
]

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
    profile = tempfile.mkdtemp(prefix="lo_va_")
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
        for path, mod in zip(PATHS, ("Module1", "Module2", "Module3")):
            with open(path, encoding="utf-8") as f:
                lib.insertByName(mod, f.read())
        sp = doc.getScriptProvider()
        for mod, fn, args, expect in PROBES:
            url = "vnd.sun.star.script:CT.%s.%s?language=Basic&location=document" % (mod, fn)
            try:
                res = sp.getScript(url).invoke(args, (), ())[0]
                ok = (res is not None) if expect is None else (res == expect)
                print("[%-8s %-16s] %s -> %r" % (mod, fn, "OK   " if ok else "FOUT?", res))
            except Exception as e:
                print("[%-8s %-16s] FOUT -> %s: %s" % (mod, fn, type(e).__name__, getattr(e, "Message", str(e))))
        doc.close(False)
    finally:
        try: proc.terminate()
        except Exception: pass

main()
