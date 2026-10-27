param([switch]$DryRun)

$ErrorActionPreference = 'Stop'
$root = [System.IO.Path]::GetFullPath($PSScriptRoot)
$targets = @(
    @{ Name = 'Backend'; Port = 8765; Script = (Join-Path $root 'backend\server.py'); ProcessNames = @('python.exe', 'pythonw.exe') },
    @{ Name = 'Frontend'; Port = 5173; Script = (Join-Path $root 'frontend\server.mjs'); ProcessNames = @('node.exe') }
)

function Test-GibleEndpoint([int]$port) {
    $path = if ($port -eq 8765) { '/api/profiles' } else { '/' }
    $request = [System.Net.HttpWebRequest]::Create("http://127.0.0.1:$port$path")
    $request.Proxy = $null
    $request.Timeout = 1000
    $request.ReadWriteTimeout = 1000
    try {
        $response = $request.GetResponse()
        try {
            $reader = New-Object System.IO.StreamReader($response.GetResponseStream())
            try { $body = $reader.ReadToEnd() } finally { $reader.Dispose() }
            if ($port -eq 8765) {
                $server = $response.Headers['Server']
                if ($server -notmatch '^(GibleLocalHTTP|PartnerLocalHTTP)/') { return $false }
                $payload = ConvertFrom-Json $body
                return (($payload.PSObject.Properties.Name -contains 'profiles') -and
                        ($payload.profiles -is [array]))
            }
            return (($body.Contains('<title>Gible</title>') -or
                     $body.Contains('<title>Partner</title>')) -and
                    $body.Contains('/src/main.js'))
        } finally { $response.Dispose() }
    } catch { return $false }
}

function Get-Listeners([int]$port) {
    @(Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue |
      Select-Object -ExpandProperty OwningProcess -Unique)
}

$failed = $false
foreach ($target in $targets) {
    $owners = @(Get-Listeners $target.Port)
    if ($owners.Count -eq 0) {
        Write-Host "$($target.Name): no server on port $($target.Port)."
        continue
    }
    foreach ($processId in $owners) {
        $process = Get-CimInstance Win32_Process -Filter "ProcessId = $processId"
        if ($null -eq $process) { continue }
        $nameMatches = $target.ProcessNames -contains $process.Name.ToLowerInvariant()
        $scriptMatches = $process.CommandLine -and
            $process.CommandLine.Replace('/', '\').IndexOf(
                $target.Script.Replace('/', '\'),
                [System.StringComparison]::OrdinalIgnoreCase) -ge 0
        if (-not $nameMatches -or (-not $scriptMatches -and -not (Test-GibleEndpoint $target.Port))) {
            [Console]::Error.WriteLine("Port $($target.Port) belongs to PID $processId ($($process.Name)), not a recognized Gible server. It was left running.")
            $failed = $true
            continue
        }
        if ($DryRun) {
            Write-Host "Would stop $($target.Name) (PID $processId) on port $($target.Port)."
            continue
        }
        try {
            Stop-Process -Id $processId -Force -ErrorAction Stop
            Write-Host "Stopped $($target.Name) (PID $processId)."
        } catch {
            [Console]::Error.WriteLine("Could not stop $($target.Name) (PID $processId): $($_.Exception.Message)")
            $failed = $true
        }
    }
    if (-not $DryRun) {
        $deadline = (Get-Date).AddSeconds(5)
        while ((Get-Listeners $target.Port).Count -gt 0 -and (Get-Date) -lt $deadline) {
            Start-Sleep -Milliseconds 200
        }
        if ((Get-Listeners $target.Port).Count -gt 0) {
            [Console]::Error.WriteLine("Port $($target.Port) is still occupied. Restart was cancelled.")
            $failed = $true
        }
    }
}

if ($failed) { exit 1 }
exit 0
