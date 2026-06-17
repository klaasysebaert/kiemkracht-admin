import time, subprocess, tempfile, uno
from com.sun.star.beans import PropertyValue

SOFFICE = r"C:\Program Files\LibreOffice\program\soffice.exe"
PORT = "2108"

TEST_BAS = r'''Function TestKoffieDir() As String
    Dim sMap As String
    Dim s As String
    Dim sNaam As String
    sMap = "C:\Users\klaas\Documents\Zaak\Afzet\Samenstelling en bestellingen\Samenstelling en bestellingen 2026\2026_week_25_koffie\"
    s = "FileExists(map+backslash)=" & FileExists(sMap)
    Dim aDagen(1) As String
    aDagen(0) = "donderdag" : aDagen(1) = "vrijdag"
    Dim d As Integer
    For d = 0 To 1
        sNaam = Dir(sMap & "*_orderpicking_afhaalpunt_" & aDagen(d) & ".odt")
        Do While sNaam <> ""
            s = s & Chr(10) & "  MATCH " & aDagen(d) & ": " & sNaam
            sNaam = Dir()
        Loop
    Next d
    TestKoffieDir = s
End Function'''

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

profile = tempfile.mkdtemp(prefix="lo_t_")
proc = boot(profile)
try:
    ctx = connect()
    smgr = ctx.ServiceManager
    p = PropertyValue(); p.Name = "Hidden"; p.Value = True
    desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
    doc = desktop.loadComponentFromURL("private:factory/scalc", "_blank", 0, (p,))
    libs = doc.BasicLibraries
    if libs.hasByName("CT"): libs.removeLibrary("CT")
    libs.createLibrary("CT"); libs.loadLibrary("CT")
    libs.getByName("CT").insertByName("T", TEST_BAS)
    sp = doc.getScriptProvider()
    script = sp.getScript("vnd.sun.star.script:CT.T.TestKoffieDir?language=Basic&location=document")
    res = script.invoke((), (), ())
    print(res[0])
    doc.close(False)
finally:
    try: proc.terminate()
    except Exception: pass
