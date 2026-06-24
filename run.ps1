# Origami Engine — PowerShell runner
# Usage from System32 or anywhere: .\run.ps1 qualify
#         or:                       .\run.ps1 all
# Requires: ANTHROPIC_API_KEY set in your env or .env loaded first

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("icp","campaigns","qualify","sequence","export","all","status")]
    [string]$Step,
    [int]$CampaignId = 1,
    [string]$Url = "https://www.scriptmasterlabs.com"
)

$ErrorActionPreference = "Stop"

function Run-Step($cmd) {
    Write-Host "`n==> $cmd" -ForegroundColor Cyan
    Invoke-Expression $cmd
    if ($LASTEXITCODE -ne 0) { throw "Step failed: $cmd" }
}

switch ($Step) {
    "icp"       { Run-Step "python -m origami.cli icp $Url" }
    "campaigns" { Run-Step "python -m origami.cli campaigns" }
    "qualify"   { Run-Step "python -m origami.cli qualify $CampaignId" }
    "sequence"  { Run-Step "python -m origami.cli sequence $CampaignId" }
    "export"    { Run-Step "python -m origami.cli export $CampaignId" }
    "status"    { Run-Step "python -m origami.cli list $CampaignId" }
    "all" {
        Run-Step "python -m origami.cli qualify $CampaignId"
        Run-Step "python -m origami.cli sequence $CampaignId"
        Run-Step "python -m origami.cli export $CampaignId"
    }
}

Write-Host "`nDone." -ForegroundColor Green
