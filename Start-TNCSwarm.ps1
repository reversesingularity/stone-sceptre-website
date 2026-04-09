<#
.SYNOPSIS
    TNC Swarm Startup -- Launches all Python servers + Nemoclaw daemon for The Nephilim Chronicles.
    Docker containers (n8n, Qdrant, Ollama, Postgres) auto-start via restart=unless-stopped.

.DESCRIPTION
    Starts the 7 Python HTTP servers (ports 8765-8771) and the Nemoclaw background daemon
    as hidden background processes. Waits for Docker infrastructure to be ready, then launches
    servers sequentially with health-check verification.

    Run manually:   .\Start-TNCSwarm.ps1
    Register as scheduled task (at logon):
        .\Start-TNCSwarm.ps1 -Register
    Unregister:
        .\Start-TNCSwarm.ps1 -Unregister

.NOTES
    Machine: DESKTOP-SINGULA
    Project: The Nephilim Chronicles v2.0 HAWK Swarm
#>

param(
    [switch]$Register,
    [switch]$Unregister,
    [int]$DockerTimeoutSeconds = 120
)

$ErrorActionPreference = 'Stop'

# --- Paths ---
$ProjectRoot = 'F:\Projects-cmodi.000\book_writer_ai_toolkit\output\nephilim_chronicles'
$Python       = Join-Path $ProjectRoot '.venv\Scripts\python.exe'
$LogDir       = Join-Path $ProjectRoot 'LOGS'
$TaskName     = 'TNC_Swarm_Startup'

# --- Service definitions ---
$Services = @(
    @{ Name = 'canon_search_api';        Script = 'canon_search_api.py';        Port = 8765 }
    @{ Name = 'kdp_format_server';       Script = 'kdp_format_server.py';       Port = 8766 }
    @{ Name = 'update_story_prototype';  Script = 'update_story_prototype.py';  Port = 8767 }
    @{ Name = 'nemotron_tool_router';    Script = 'nemotron_tool_router.py';    Port = 8768 }
    @{ Name = 'utility_server';          Script = 'utility_server.py';          Port = 8769 }
    @{ Name = 'theological_guard_server';Script = 'theological_guard_server.py';Port = 8770 }
    @{ Name = 'conductor_server';        Script = 'conductor_server.py';        Port = 8771 }
)

$Daemon = @{ Name = 'nemoclaw_daemon'; Script = 'nemoclaw_daemon.py' }

# --- Task Scheduler registration ---
if ($Register) {
    # Check for admin rights; self-elevate if needed
    $isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if (-not $isAdmin) {
        Write-Host "[INFO] Elevating to admin for scheduled task registration..." -ForegroundColor Cyan
        Start-Process powershell -Verb RunAs -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`" -Register" -Wait
        # Check if the task now exists
        $check = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        if ($check) {
            Write-Host "[OK] Scheduled task '$TaskName' registered. Swarm will start at every logon." -ForegroundColor Green
        } else {
            Write-Host "[FAIL] Task registration failed or was cancelled." -ForegroundColor Red
        }
        exit 0
    }

    $Action  = New-ScheduledTaskAction `
        -Execute 'powershell.exe' `
        -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$PSScriptRoot\Start-TNCSwarm.ps1`"" `
        -WorkingDirectory $ProjectRoot

    $Trigger = New-ScheduledTaskTrigger -AtLogon

    $Settings = New-ScheduledTaskSettingsSet `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -StartWhenAvailable `
        -ExecutionTimeLimit (New-TimeSpan -Hours 0)

    Register-ScheduledTask `
        -TaskName $TaskName `
        -Action $Action `
        -Trigger $Trigger `
        -Settings $Settings `
        -Description 'Starts The Nephilim Chronicles v2.0 HAWK Swarm (7 Python servers + Nemoclaw daemon)' `
        -Force `
        -ErrorAction Stop

    Write-Host "[OK] Scheduled task '$TaskName' registered. Swarm will start at every logon." -ForegroundColor Green
    exit 0
}

if ($Unregister) {
    $isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if (-not $isAdmin) {
        Write-Host "[INFO] Elevating to admin for task removal..." -ForegroundColor Cyan
        Start-Process powershell -Verb RunAs -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`" -Unregister" -Wait
        exit 0
    }
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "[OK] Scheduled task '$TaskName' removed." -ForegroundColor Yellow
    exit 0
}

# --- Ensure log directory ---
if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir -Force | Out-Null }

$StartupLog = Join-Path $LogDir "swarm_startup_$(Get-Date -Format 'yyyy-MM-dd_HHmmss').log"

function Log($msg) {
    $line = "[$(Get-Date -Format 'HH:mm:ss')] $msg"
    Write-Host $line
    Add-Content -Path $StartupLog -Value $line
}

# --- Phase 1: Wait for Docker infrastructure ---
Log "=== TNC Swarm Startup ==="
Log "Phase 1: Waiting for Docker infrastructure..."

$DockerContainers = @('n8n', 'qdrant', 'ollama', 'self-hosted-ai-starter-kit-postgres-1')
$deadline = (Get-Date).AddSeconds($DockerTimeoutSeconds)

foreach ($container in $DockerContainers) {
    $ready = $false
    while (-not $ready -and (Get-Date) -lt $deadline) {
        try {
            $status = docker inspect --format '{{.State.Running}}' $container 2>$null
            if ($status -eq 'true') {
                Log "  [OK] $container is running"
                $ready = $true
            } else {
                Start-Sleep -Seconds 3
            }
        } catch {
            Start-Sleep -Seconds 3
        }
    }
    if (-not $ready) {
        Log "  [WARN] $container not ready after ${DockerTimeoutSeconds}s -- continuing anyway"
    }
}

# --- Phase 2: Kill any orphaned Python servers ---
Log "Phase 2: Checking for orphaned processes..."

foreach ($svc in $Services) {
    $existing = Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
        Where-Object { $_.LocalPort -eq $svc.Port }
    if ($existing) {
        $pid = $existing.OwningProcess
        Log "  [WARN] Port $($svc.Port) in use by PID $pid -- killing orphan"
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
        Start-Sleep -Milliseconds 500
    }
}

# --- Phase 3: Start Python servers ---
Log "Phase 3: Starting Python servers..."

foreach ($svc in $Services) {
    $scriptPath = Join-Path $ProjectRoot $svc.Script
    $logFile    = Join-Path $LogDir "$($svc.Name).log"

    $proc = Start-Process -FilePath $Python `
        -ArgumentList $scriptPath `
        -WorkingDirectory $ProjectRoot `
        -WindowStyle Hidden `
        -RedirectStandardOutput $logFile `
        -RedirectStandardError (Join-Path $LogDir "$($svc.Name)_err.log") `
        -PassThru

    Log "  Started $($svc.Name) on :$($svc.Port) (PID $($proc.Id))"
    Start-Sleep -Seconds 1
}

# --- Phase 4: Start Nemoclaw daemon ---
Log "Phase 4: Starting Nemoclaw daemon..."

$daemonScript = Join-Path $ProjectRoot $Daemon.Script
$daemonLog    = Join-Path $LogDir "$($Daemon.Name).log"

$daemonProc = Start-Process -FilePath $Python `
    -ArgumentList "$daemonScript --log-level INFO" `
    -WorkingDirectory $ProjectRoot `
    -WindowStyle Hidden `
    -RedirectStandardOutput $daemonLog `
    -RedirectStandardError (Join-Path $LogDir "$($Daemon.Name)_err.log") `
    -PassThru

Log "  Started $($Daemon.Name) (PID $($daemonProc.Id))"

# --- Phase 5: Health verification ---
Log "Phase 5: Health verification (15s warmup)..."
Start-Sleep -Seconds 15

$results = @()
foreach ($svc in $Services) {
    $listening = Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
        Where-Object { $_.LocalPort -eq $svc.Port }
    if ($listening) { $status = 'UP' } else { $status = 'DOWN' }
    $results += [PSCustomObject]@{ Service = $svc.Name; Port = $svc.Port; Status = $status }
    Log "  $($svc.Name):$($svc.Port) -- $status"
}

$daemonAlive = -not $daemonProc.HasExited
if ($daemonAlive) { $daemonStatus = 'UP' } else { $daemonStatus = 'DOWN' }
$results += [PSCustomObject]@{ Service = 'nemoclaw_daemon'; Port = 'N/A'; Status = $daemonStatus }
Log "  nemoclaw_daemon -- $daemonStatus"

$upCount   = ($results | Where-Object Status -eq 'UP').Count
$totalCount = $results.Count

Log "=== Startup complete: $upCount / $totalCount services running ==="
Log "Log: $StartupLog"
