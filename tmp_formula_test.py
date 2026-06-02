import os, sys, time, subprocess, tempfile, uno
from com.sun.star.beans import PropertyValue

SOFFICE = r"C:\Program Files\LibreOffice\program\soffice.exe"
PROFILE = tempfile.mkdtemp(prefix="lo_test_")
PORT = "2103"

def boot():
    args = [SOFFICE, "--headless", "--norestore", "--invisible", "--nologo",
            "--nofirststartwizard",
            "-env:UserInstallation=file:///" + PROFILE.replace("\\", "/"),
            "--accept=socket,host=localhost,port=%s;urp;" % PORT]
    return subprocess.Popen(args)

def connect():
    localContext = uno.getComponentContext()
    resolver = localContext.ServiceManager.createInstanceWithContext(
        "com.sun.star.bridge.UnoUrlResolver", localContext)
    last = None
    for _ in range(60):
        try:
            ctx = resolver.resolve(
                "uno:socket,host=localhost,port=%s;urp;StarOffice.ComponentContext" % PORT)
            return ctx
        except Exception as e:
            last = e
            time.sleep(1)
    raise RuntimeError("kon niet verbinden: %s" % last)

def main():
    proc = boot()
    try:
        ctx = connect()
        smgr = ctx.ServiceManager
        desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
        p = PropertyValue(); p.Name = "Hidden"; p.Value = True
        doc = desktop.loadComponentFromURL("private:factory/scalc", "_blank", 0, (p,))
        sheet = doc.Sheets.getByIndex(0)
        cell = sheet.getCellByPosition(0, 0)

        # ontdek het scheidingsteken dat dit profiel gebruikt
        tests = []
        for sep in (";", ","):
            f = ('=TEXTJOIN(CHAR(10){s}1{s}'
                 'IF(B1=""{s}""{s}"x: "&B1){s}'
                 'IF(C1=""{s}""{s}"y: "&C1))').format(s=sep)
            try:
                cell.setFormula(f)
                got = cell.getFormula()
                tests.append("sep=%r  OK   -> %s" % (sep, got))
            except Exception as e:
                tests.append("sep=%r  FOUT -> %s: %s" % (sep, type(e).__name__, e))
            cell.setString("")

        # ook even een gewone IF/SUM (zoals bestaande werkende calls)
        try:
            cell.setFormula("=IF(B1=\"\";\"\";SUM(B1:C1))")
            tests.append("ctrl IF/SUM ;  OK -> %s" % cell.getFormula())
        except Exception as e:
            tests.append("ctrl IF/SUM ;  FOUT -> %s: %s" % (type(e).__name__, e))

        print("\n".join(tests))
        doc.close(False)
    finally:
        try:
            proc.terminate()
        except Exception:
            pass

main()
