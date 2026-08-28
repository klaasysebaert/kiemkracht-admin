# Zet de LibreOffice-configuratie uit lo-config-backup\ terug in het
# gebruikersprofiel. Bedoeld voor een verse installatie of na een crash die de
# instellingen wiste.
#
# Gebruik: .\herstel-lo-config.ps1
#
# WAT DIT WEL DOET
#   - de menubalk en werkbalken van Calc/Writer terugzetten (soffice.cfg)
#
# WAT DIT NIET DOET
#   - de macro's zelf: die zet je met .\sync-macro.ps1 op hun plek, rechtstreeks
#     uit de bronbestanden in deze map. Doe dat eerst; het menu verwijst naar
#     Standard.Module2.Start*, dus zonder macro's wijzen de items naar niets.
#
# LibreOffice MOET afgesloten zijn: bij het afsluiten schrijft LO zijn eigen
# versie van deze bestanden terug en overschrijft het je herstel.

$ErrorActionPreference = "Stop"

if (Get-Process soffice* -ErrorAction SilentlyContinue) {
    Write-Output "LibreOffice draait. Sluit het volledig af en probeer opnieuw --"
    Write-Output "anders overschrijft LO bij het afsluiten wat dit script terugzet."
    exit 1
}

$backupDir = "$PSScriptRoot\lo-config-backup"
$cfgDir    = "$env:APPDATA\LibreOffice\4\user\config\soffice.cfg\modules"

if (-not (Test-Path $backupDir)) {
    Write-Output "Geen map lo-config-backup gevonden naast dit script."
    exit 1
}

$bestanden = @(
    @{ Bron = "scalc-menubar.xml";       Doel = "$cfgDir\scalc\menubar\menubar.xml" },
    @{ Bron = "scalc-standardbar.xml";   Doel = "$cfgDir\scalc\toolbar\standardbar.xml" },
    @{ Bron = "swriter-standardbar.xml"; Doel = "$cfgDir\swriter\toolbar\standardbar.xml" }
)

$hersteld = 0
foreach ($b in $bestanden) {
    $bron = "$backupDir\$($b.Bron)"
    if (-not (Test-Path $bron)) {
        Write-Output "  overgeslagen (niet in de back-up): $($b.Bron)"
        continue
    }
    $doelMap = Split-Path $b.Doel -Parent
    if (-not (Test-Path $doelMap)) { New-Item -ItemType Directory -Path $doelMap -Force | Out-Null }
    Copy-Item $bron $b.Doel -Force
    Write-Output "  $($b.Bron) -> $($b.Doel)"
    $hersteld++
}

Write-Output ""
if ($hersteld -eq 0) {
    Write-Output "Niets hersteld."
} else {
    Write-Output "$hersteld bestand(en) hersteld. Start LibreOffice; de menu's"
    Write-Output "Kiemkracht (weekbestand) en Kiemkracht (samenstelling) horen er te staan."
    Write-Output "Ontbreken de macro's nog? Draai dan eerst .\sync-macro.ps1."
}
