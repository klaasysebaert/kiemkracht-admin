import os, time, subprocess, tempfile, uno

SOFFICE = r"C:\Program Files\LibreOffice\program\soffice.exe"
PROFILE = tempfile.mkdtemp(prefix="lo_ct_")
PORT = "2104"
BASPATH = r"C:\Users\klaas\projects\kiemkracht-admin\macro-kiemkracht-Module1"

def boot():
    args = [SOFFICE, "--headless", "--norestore", "--invisible", "--nologo",
            "--nofirststartwizard",
            "-env:UserInstallation=file:///" + PROFILE.replace("\\", "/"),
            "--accept=socket,host=localhost,port=%s;urp;" % PORT]
    return subprocess.Popen(args)

def connect():
    lc = uno.getComponentContext()
    resolver = lc.ServiceManager.createInstanceWithContext(
        "com.sun.star.bridge.UnoUrlResolver", lc)
    last = None
    for _ in range(60):
        try:
            return resolver.resolve(
                "uno:socket,host=localhost,port=%s;urp;StarOffice.ComponentContext" % PORT)
        except Exception as e:
            last = e; time.sleep(1)
    raise RuntimeError("verbinden faalde: %s" % last)

def main():
    with open(BASPATH, "r", encoding="utf-8") as f:
        code = f.read()
    proc = boot()
    try:
        ctx = connect()
        smgr = ctx.ServiceManager
        from com.sun.star.beans import PropertyValue
        p = PropertyValue(); p.Name = "Hidden"; p.Value = True
        desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
        doc = desktop.loadComponentFromURL("private:factory/scalc", "_blank", 0, (p,))

        libs = doc.BasicLibraries
        if libs.hasByName("CT"):
            libs.removeLibrary("CT")
        libs.createLibrary("CT")
        libs.loadLibrary("CT")
        lib = libs.getByName("CT")
        lib.insertByName("Module1", code)

        # forceer compilatie door een onschuldige Function aan te roepen
        sp = doc.getScriptProvider()
        url = "vnd.sun.star.script:CT.Module1.KolomLetter?language=Basic&location=document"
        script = sp.getScript(url)
        try:
            res = script.invoke((5,), (), ())
            print("COMPILE OK  -> KolomLetter(5) =", res[0])
        except Exception as e:
            print("FOUT bij compile/run:")
            print(type(e).__name__)
            msg = getattr(e, "Message", None) or str(e)
            print(msg)
    finally:
        try: proc.terminate()
        except Exception: pass

main()
