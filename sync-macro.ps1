# Synchroniseert alle macro's naar de LibreOffice-gebruikersbibliotheek
# Gebruik: .\sync-macro.ps1
#
# TWEE SOORTEN BESTANDEN, MET VERSCHILLEND GEDRAG
# -----------------------------------------------
#   .xba (+ script.xlb)  LibreOffice' eigen opslagformaat. LO houdt de
#                        bibliotheken in het GEHEUGEN en schrijft ze bij het
#                        afsluiten terug naar schijf. Schrijf je een .xba
#                        terwijl LO draait, dan overschrijft LO die bij het
#                        afsluiten weer met zijn oude versie -- de sync lijkt
#                        gelukt maar is stil verdwenen.
#   .bas                 Bestaat enkel voor deze sync: ReloadKiemkracht /
#                        ReloadStandard lezen ze via LeesBasUtf8 en duwen de
#                        code met replaceByName in de draaiende LO. LO schrijft
#                        .bas NOOIT zelf (bewijs: Standard\Module2 en Module3
#                        hebben Bas = $false en hebben dus geen .bas-bestand).
#                        Ze zijn dus altijd veilig te schrijven.
#
# Daarom: draait LO, dan schrijft dit script ALLEEN de .bas-bestanden (zodat de
# hot-reload deze sessie werkt) en LAAT het de .xba's met rust. Zo blijft wat op
# schijf staat gelijk aan wat LO in het geheugen heeft, en valt er bij het
# afsluiten niets te overschrijven. Het script meldt dan wat nog niet is
# doorgevoerd en eindigt met exitcode 2.
#
# LET OP -- Standard\Module2 (alle Start*-wrappers) heeft geen .bas en wordt
# door niets hot-reloaded: ReloadStandard herlaadt enkel Standard Module1,
# ReloadKiemkracht enkel de Kiemkracht-bibliotheek. Een NIEUWE Start*-wrapper
# komt dus pas beschikbaar na een sync met LO gesloten + een herstart van LO.
# (Module2 hot-reloaden kan ook niet zomaar: de reload-code draait zelf in dat
# module, en je eigen module vervangen tijdens de uitvoering breekt de run.)

$libDir    = "$env:APPDATA\LibreOffice\4\user\basic\Kiemkracht"
$stdDir    = "$env:APPDATA\LibreOffice\4\user\basic\Standard"
$utf8NoBom = [System.Text.UTF8Encoding]::new($false)

# Draait LibreOffice? (soffice.exe en soffice.bin)
$loProc = Get-Process -Name soffice* -ErrorAction SilentlyContinue
$loOpen = [bool]$loProc

# Alle modules: project -> LO
# Bas = $true: ook .bas wegschrijven (voor hot-reload via replaceByName)
$modules = @(
    @{ Source = "$PSScriptRoot\macro-kiemkracht-Module1"; Name = "Module1"; Dir = $libDir; Bas = $true  },
    @{ Source = "$PSScriptRoot\macro-kiemkracht-Module2"; Name = "Module2"; Dir = $libDir; Bas = $true  },
    @{ Source = "$PSScriptRoot\macro-kiemkracht-Module3"; Name = "Module3"; Dir = $libDir; Bas = $true  },
    @{ Source = "$PSScriptRoot\macro-kiemkracht-Module4"; Name = "Module4"; Dir = $libDir; Bas = $true  },
    @{ Source = "$PSScriptRoot\macro-kiemkracht-Module5"; Name = "Module5"; Dir = $libDir; Bas = $true  },
    @{ Source = "$PSScriptRoot\macro-kiemkracht-Module6"; Name = "Module6"; Dir = $libDir; Bas = $true  },
    @{ Source = "$PSScriptRoot\macro-Standard-Module1";   Name = "Module1"; Dir = $stdDir; Bas = $true  },
    @{ Source = "$PSScriptRoot\macro-Standard-Module2";   Name = "Module2"; Dir = $stdDir; Bas = $false },
    @{ Source = "$PSScriptRoot\macro-Standard-Module3";   Name = "Module3"; Dir = $stdDir; Bas = $false }
)

$uitgesteld = @()   # modules waarvan de .xba nog moet worden weggeschreven

foreach ($m in $modules) {
    if (-not (Test-Path $m.Source)) { continue }
    $code    = [System.IO.File]::ReadAllText($m.Source, [System.Text.Encoding]::UTF8)
    $codeXml = $code.Replace("&", "&amp;").Replace("<", "&lt;").Replace(">", "&gt;")
    $xba = '<?xml version="1.0" encoding="UTF-8"?>' + "`r`n" +
           '<!DOCTYPE script:module PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "module.dtd">' + "`r`n" +
           '<script:module xmlns:script="http://openoffice.org/2000/script" script:name="' + $m.Name + '" script:language="StarBasic">' +
           $codeXml + '</script:module>'
    $xbaPad = "$($m.Dir)\$($m.Name).xba"
    $label  = (Split-Path $m.Dir -Leaf) + "\" + $m.Name

    if ($loOpen) {
        # .xba overslaan: LO zou hem bij het afsluiten toch overschrijven.
        # Wel melden of er iets te schrijven vàlt, zodat de waarschuwing klopt.
        $huidig = ""
        if (Test-Path $xbaPad) {
            $huidig = [System.IO.File]::ReadAllText($xbaPad, [System.Text.Encoding]::UTF8)
        }
        if ($huidig -ne $xba) { $uitgesteld += $label }
    } else {
        [System.IO.File]::WriteAllText($xbaPad, $xba, $utf8NoBom)
    }

    if ($m.Bas) {
        [System.IO.File]::WriteAllText("$($m.Dir)\$($m.Name).bas", $code, $utf8NoBom)
    }
    Write-Output "  $label <- $($m.Source)"
}

if ($loOpen) {
    Write-Output "Alleen de .bas-bestanden geschreven (LibreOffice draait)."
} else {
    Write-Output "Gesynchroniseerd (.bas en .xba)."
}

# Kiemkracht script.xlb bijwerken (LO overschrijft dit bij afsluiten)
if (-not $loOpen) {
    $xlbKiemkracht = "$libDir\script.xlb"
    $xlbInhoud = '<?xml version="1.0" encoding="UTF-8"?>' + "`r`n" +
        '<!DOCTYPE library:library PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "library.dtd">' + "`r`n" +
        '<library:library xmlns:library="http://openoffice.org/2000/library" library:name="Kiemkracht" library:readonly="false" library:passwordprotected="false">' + "`r`n" +
        ' <library:element library:name="Module1"/>' + "`r`n" +
        ' <library:element library:name="Module2"/>' + "`r`n" +
        ' <library:element library:name="Module3"/>' + "`r`n" +
        ' <library:element library:name="Module4"/>' + "`r`n" +
        ' <library:element library:name="Module5"/>' + "`r`n" +
        ' <library:element library:name="Module6"/>' + "`r`n" +
        '</library:library>'
    [System.IO.File]::WriteAllText($xlbKiemkracht, $xlbInhoud, $utf8NoBom)
    Write-Output "  Kiemkracht\script.xlb bijgewerkt."
}

# Back-up van LO-configuratiebestanden die bij een crash gewist worden.
# Enkel met LO gesloten: anders back-up je LO's geheugenversie over de zonet
# gesynchroniseerde versie heen, en is de back-up net het oude bestand.
if (-not $loOpen) {
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
}

# Hot-reload in de draaiende LO-instantie (leest de .bas die we net schreven)
if ($loOpen) {
    $soffice = $null
    foreach ($pad in @(
        "$env:ProgramFiles\LibreOffice\program\soffice.exe",
        "$([System.Environment]::GetEnvironmentVariable('ProgramFiles(x86)'))\LibreOffice\program\soffice.exe"
    )) {
        if (Test-Path $pad) { $soffice = $pad; break }
    }
    if ($soffice) {
        & $soffice "macro:///Standard.Module2.StartReloadStandard"
        Write-Output "Standard Module1 + Kiemkracht-modules herladen in LibreOffice."
    } else {
        Write-Output "soffice.exe niet gevonden; voer StartReloadStandard manueel uit."
    }

    Write-Output ""
    Write-Output "=============================================================="
    Write-Output " LET OP: LIBREOFFICE DRAAIT - SYNC IS NIET VOLLEDIG"
    Write-Output "=============================================================="
    if ($uitgesteld.Count -gt 0) {
        Write-Output " Deze modules staan nog NIET in de bibliotheek op schijf:"
        foreach ($u in $uitgesteld) { Write-Output "   - $u" }
    } else {
        Write-Output " Geen .xba-wijzigingen open - de bibliotheek op schijf is bij."
    }
    Write-Output ""
    Write-Output " De hot-reload hierboven geldt alleen voor DEZE LO-sessie."
    Write-Output " Nieuwe Start*-wrappers (Standard\Module2) werken pas na:"
    Write-Output "   1. LibreOffice VOLLEDIG afsluiten"
    Write-Output "   2. .\sync-macro.ps1 opnieuw draaien"
    Write-Output "   3. LibreOffice heropenen"
    Write-Output "=============================================================="
    exit 2
} else {
    Write-Output "LibreOffice niet open; alles staat klaar voor de volgende start."
    exit 0
}
