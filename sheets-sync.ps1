param(
    [string]$Mode,        # "read" of "write"
    [string]$WebAppUrl,
    [string]$DataFile,    # temp TSV-bestand
    [string]$DoneFile     # sentinel: bestaat zodra klaar
)

if ($Mode -eq "read") {
    try {
        $r = Invoke-WebRequest -Uri $WebAppUrl -UseBasicParsing
        [System.IO.File]::WriteAllText($DataFile, $r.Content, [System.Text.Encoding]::UTF8)
    } catch {
        [System.IO.File]::WriteAllText($DataFile, "ERROR:$_", [System.Text.Encoding]::UTF8)
    }
} elseif ($Mode -eq "write") {
    try {
        $body = [System.IO.File]::ReadAllText($DataFile, [System.Text.Encoding]::UTF8)
        Invoke-WebRequest -Uri $WebAppUrl -Method POST -Body $body `
            -ContentType "text/plain; charset=utf-8" -UseBasicParsing | Out-Null
    } catch { }
}

[System.IO.File]::WriteAllText($DoneFile, "DONE", [System.Text.Encoding]::UTF8)
