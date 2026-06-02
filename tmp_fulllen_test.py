import time, subprocess, tempfile, uno
from com.sun.star.beans import PropertyValue

SOFFICE = r"C:\Program Files\LibreOffice\program\soffice.exe"
PROFILE = tempfile.mkdtemp(prefix="lo_fl_")
PORT = "2105"

def kolomletter(i):
    s = ""
    while True:
        s = chr(65 + (i % 26)) + s
        i = i // 26 - 1
        if i < 0:
            break
    return s

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

def build(ngro, sep):
    sData = "'Week 23 - 2026'"
    asr = 7
    cGroent0 = 24
    a = "à"; eur = "€"
    parts = []
    for gd in range(ngro):
        col = kolomletter(cGroent0 + gd)
        unit = kolomletter(gd)
        p = ('IF({d}.{c}{r}=""{s}""{s}{d}.{c}$2&": "&{d}.{c}{r}&" "&Blad2.{u}$100&" {a} "&'
             'TEXT({d}.{c}$3{s}"0,00")&" {e} = "&TEXT({d}.{c}{r}*{d}.{c}$3{s}"0,00")&" {e}")'
             ).format(d=sData, c=col, r=asr, u=unit, s=sep, a=a, e=eur)
        parts.append(p)
    return "=TEXTJOIN(CHAR(10){s}1{s}{body})".format(s=sep, body=sep.join(parts))

def main():
    proc = boot()
    try:
        ctx = connect()
        smgr = ctx.ServiceManager
        p = PropertyValue(); p.Name = "Hidden"; p.Value = True
        desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
        doc = desktop.loadComponentFromURL("private:factory/scalc", "_blank", 0, (p,))
        sheet = doc.Sheets.getByIndex(0)
        cell = sheet.getCellByPosition(22, 6)
        for ngro in (10, 20, 30, 40):
            for sep in (";", ","):
                f = build(ngro, sep)
                try:
                    cell.setFormula(f)
                    cell.setString("")
                    print("ngro=%2d sep=%r len=%4d  OK" % (ngro, sep, len(f)))
                except Exception as e:
                    print("ngro=%2d sep=%r len=%4d  FOUT -> %s: %s" % (
                        ngro, sep, len(f), type(e).__name__, getattr(e, "Message", str(e))))
        doc.close(False)
    finally:
        try: proc.terminate()
        except Exception: pass

main()
