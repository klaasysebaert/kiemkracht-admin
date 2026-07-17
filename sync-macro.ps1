# Synchroniseert alle macro's naar LibreOffice gebruikersbibliotheek
# Gebruik: .\sync-macro.ps1
# Als LibreOffice open staat: de Start*-wrappers herladen automatisch bij uitvoering.
# Als LibreOffice gesloten is: gewoon heropenen.

$libDir    = "$env:APPDATA\LibreOffice\4\user\basic\Kiemkracht"
$stdDir    = "$env:APPDATA\LibreOffice\4\user\basic\Standard"
$utf8NoBom = [System.Text.UTF8Encoding]::new($false)

# Alle modules: project -> LO
# Bas = $true: ook .bas wegschrijven (voor hot-reload via replaceByName)
$modules = @(
    @{ Source = "$PSScriptRoot\macro-kiemkracht-Module1"; Name = "Module1"; Dir = $libDir; Bas = $true  },
    @{ Source = "$PSScriptRoot\macro-kiemkracht-Module2"; Name = "Module2"; Dir = $libDir; Bas = $true  },
    @{ Source = "$PSScriptRoot\macro-kiemkracht-Module3"; Name = "Module3"; Dir = $libDir; Bas = $true  },
    @{ Source = "$PSScriptRoot\macro-kiemkracht-Module4"; Name = "Module4"; Dir = $libDir; Bas = $true  },
    @{ Source = "$PSScriptRoot\macro-kiemkracht-Module5"; Name = "Module5"; Dir = $libDir; Bas = $true  },
    @{ Source = "$PSScriptRoot\macro-Standard-Module1";   Name = "Module1"; Dir = $stdDir; Bas = $true  },
    @{ Source = "$PSScriptRoot\macro-Standard-Module2";   Name = "Module2"; Dir = $stdDir; Bas = $false },
    @{ Source = "$PSScriptRoot\macro-Standard-Module3";   Name = "Module3"; Dir = $stdDir; Bas = $false }
)

foreach ($m in $modules) {
    if (-not (Test-Path $m.Source)) { continue }
    $code    = [System.IO.File]::ReadAllText($m.Source, [System.Text.Encoding]::UTF8)
    $codeXml = $code.Replace("&", "&amp;").Replace("<", "&lt;").Replace(">", "&gt;")
    $xba = '<?xml version="1.0" encoding="UTF-8"?>' + "`r`n" +
           '<!DOCTYPE script:module PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "module.dtd">' + "`r`n" +
           '<script:module xmlns:script="http://openoffice.org/2000/script" script:name="' + $m.Name + '" script:language="StarBasic">' +
           $codeXml + '</script:module>'
    [System.IO.File]::WriteAllText("$($m.Dir)\$($m.Name).xba", $xba, $utf8NoBom)
    if ($m.Bas) {
        [System.IO.File]::WriteAllText("$($m.Dir)\$($m.Name).bas", $code, $utf8NoBom)
    }
    Write-Output "  $($m.Name) -> $($m.Dir): $($m.Source)"
}
Write-Output "Gesynchroniseerd."

# Kiemkracht script.xlb bijwerken (LO overschrijft dit bij afsluiten)
$xlbKiemkracht = "$libDir\script.xlb"
$xlbInhoud = '<?xml version="1.0" encoding="UTF-8"?>' + "`r`n" +
    '<!DOCTYPE library:library PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "library.dtd">' + "`r`n" +
    '<library:library xmlns:library="http://openoffice.org/2000/library" library:name="Kiemkracht" library:readonly="false" library:passwordprotected="false">' + "`r`n" +
    ' <library:element library:name="Module1"/>' + "`r`n" +
    ' <library:element library:name="Module2"/>' + "`r`n" +
    ' <library:element library:name="Module3"/>' + "`r`n" +
    ' <library:element library:name="Module4"/>' + "`r`n" +
    '</library:library>'
[System.IO.File]::WriteAllText($xlbKiemkracht, $xlbInhoud, $utf8NoBom)
Write-Output "  Kiemkracht\script.xlb bijgewerkt."

# Back-up van LO-configuratiebestanden die bij een crash gewist worden
$basicDir  = "$env:APPDATA\LibreOffice\4\user\basic"
$backupDir = "$PSScriptRoot\lo-config-backup"
if (-not (Test-Path $backupDir)) { New-Item -ItemType Directory -Path $backupDir | Out-Null }
Copy-Item "$basicDir\script.xlc"               "$backupDir\script.xlc"            -Force
Copy-Item "$basicDir\Standard\script.xlb"      "$backupDir\Standard-script.xlb"   -Force
Copy-Item "$basicDir\Standard\Module1.xba"     "$backupDir\Standard-Module1.xba"  -Force
Copy-Item "$basicDir\Standard\Module2.xba"     "$backupDir\Standard-Module2.xba"  -Force
if (Test-Path "$basicDir\Standard\Module3.xba") {
    Copy-Item "$basicDir\Standard\Module3.xba" "$backupDir\Standard-Module3.xba"  -Force
}
Copy-Item "$basicDir\Kiemkracht\script.xlb"    "$backupDir\Kiemkracht-script.xlb" -Force
Write-Output "Back-up opgeslagen in lo-config-backup\"

# Hot-reload Standard Module1 in draaiende LO instantie
if (Get-Process -Name soffice -ErrorAction SilentlyContinue) {
    $soffice = $null
    foreach ($pad in @(
        "$env:ProgramFiles\LibreOffice\program\soffice.exe",
        "$([System.Environment]::GetEnvironmentVariable('ProgramFiles(x86)'))\LibreOffice\program\soffice.exe"
    )) {
        if (Test-Path $pad) { $soffice = $pad; break }
    }
    if ($soffice) {
        & $soffice "macro:///Standard.Module2.StartReloadStandard"
        Write-Output "Standard Module1 herladen in LibreOffice."
    } else {
        Write-Output "soffice.exe niet gevonden; voer StartReloadStandard manueel uit."
    }
} else {
    Write-Output "LibreOffice niet open; Standard Module1 wordt geladen bij volgende start."
}
