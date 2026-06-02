import time, subprocess, tempfile, uno
from com.sun.star.beans import PropertyValue

SOFFICE = r"C:\Program Files\LibreOffice\program\soffice.exe"
PROFILE = tempfile.mkdtemp(prefix="lo_ca_")
PORT = "2106"
BASE = r"C:\Users\klaas\projects\kiemkracht-admin"
MODS = {
    "Module1": BASE + r"\macro-kiemkracht-Module1",
    "Module2": BASE + r"\macro-kiemkracht-Module2",
    "Module3": BASE + r"\macro-kiemkracht-Module3",
}
# (module, function, args) — zuivere functies om compilatie te forceren
PROBES = [
    ("Module1", "KolomLetter", (5,)),
    ("Module2", "FmtNum2", (1.5,)),
    ("Module3", "EenheidUitRij3", ("test",)),
]

def boot():
    args = [SOFFICE, "--headless", "--norestore", "--invisible", "--nologo",
            "--nofirststartwizard",
            "-env:UserInstallation=file:///" + PROFILE.replace("\\", "/"),
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
    code = {}
    for name, path in MODS.items():
        with open(path, "r", encoding="utf-8") as f:
            code[name] = f.read()
    proc = boot()
    try:
        ctx = connect()
        smgr = ctx.ServiceManager
        p = PropertyValue(); p.Name = "Hidden"; p.Value = True
        desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
        doc = desktop.loadComponentFromURL("private:factory/scalc", "_blank", 0, (p,))
        libs = doc.BasicLibraries
        if libs.hasByName("CT"):
            libs.removeLibrary("CT")
        libs.createLibrary("CT")
        libs.loadLibrary("CT")
        lib = libs.getByName("CT")
        for name in MODS:
            lib.insertByName(name, code[name])
        sp = doc.getScriptProvider()
        for mod, fn, args in PROBES:
            url = "vnd.sun.star.script:CT.%s.%s?language=Basic&location=document" % (mod, fn)
            try:
                script = sp.getScript(url)
                res = script.invoke(args, (), ())
                print("%-8s COMPILE OK (%s -> %r)" % (mod, fn, res[0]))
            except Exception as e:
                print("%-8s COMPILE/RUN FOUT bij %s:" % (mod, fn))
                print("   ", type(e).__name__, ":", getattr(e, "Message", str(e)))
        doc.close(False)
    finally:
        try: proc.terminate()
        except Exception: pass

main()
