import time, subprocess, tempfile, uno
from com.sun.star.beans import PropertyValue

SOFFICE = r"C:\Program Files\LibreOffice\program\soffice.exe"
PORT = "2108"
BASE = r"C:\Users\klaas\projects\kiemkracht-admin"
MODS = ["Module1", "Module2", "Module3"]

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

def get_app_libs(ctx, smgr):
    tries = []
    # methode A: createInstance zonder context
    try:
        o = smgr.createInstance("com.sun.star.script.ApplicationScriptLibrary")
        tries.append(("createInstance", o))
    except Exception as e:
        tries.append(("createInstance", "EXC:%s" % e))
    # methode B: singleton via context
    try:
        o = ctx.getByName("/singletons/com.sun.star.script.theApplicationScriptLibrary")
        tries.append(("singleton theApplicationScriptLibrary", o))
    except Exception as e:
        tries.append(("singleton theApplicationScriptLibrary", "EXC:%s" % e))
    return tries

def main():
    code = {}
    for m in MODS:
        with open(BASE + "\\macro-kiemkracht-" + m, encoding="utf-8") as f:
            code[m] = f.read()
    profile = tempfile.mkdtemp(prefix="lo_al_")
    proc = boot(profile)
    try:
        ctx = connect()
        smgr = ctx.ServiceManager
        for name, obj in get_app_libs(ctx, smgr):
            print("appLibs via %-40s -> %r" % (name, obj))
        # kies de eerste werkende
        libs = None
        try:
            libs = smgr.createInstance("com.sun.star.script.ApplicationScriptLibrary")
        except Exception:
            pass
        if libs is None:
            try:
                libs = ctx.getByName("/singletons/com.sun.star.script.theApplicationScriptLibrary")
            except Exception:
                pass
        if libs is None:
            print("GEEN appLibs-container gevonden"); return
        if not libs.hasByName("CT"):
            libs.createLibrary("CT")
        libs.loadLibrary("CT")
        lib = libs.getByName("CT")
        for m in MODS:
            if lib.hasByName(m):
                lib.replaceByName(m, code[m])
            else:
                lib.insertByName(m, code[m])
        # invoke via app-script-provider
        mspf = smgr.createInstanceWithContext(
            "com.sun.star.script.provider.MasterScriptProviderFactory", ctx)
        sp = mspf.createScriptProvider("")
        url = "vnd.sun.star.script:CT.Module1.KolomLetter?language=Basic&location=application"
        try:
            res = sp.getScript(url).invoke((5,), (), ())
            print("INVOKE KolomLetter(5) =", repr(res[0]), "(geen compileerfout)")
        except Exception as e:
            print("INVOKE FOUT ->", type(e).__name__, ":", getattr(e, "Message", str(e)))
    finally:
        try: proc.terminate()
        except Exception: pass

main()
