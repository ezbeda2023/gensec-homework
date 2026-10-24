<# Prompt for a Gemini key without saving it to a source file or shell history. #>
param(
    [string]$Model = 'gemini-3.5-flash-lite'
)
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$previousModel = $env:GEMINI_MODEL
$env:GEMINI_MODEL = $Model
Write-Host "Using Gemini model: $Model"
$agentKey = Read-Host 'Gemini API key (hidden)' -AsSecureString
$keyPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($agentKey)
try {
    $env:GEMINI_API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($keyPointer)
    $uvCommand = Get-Command uv -ErrorAction SilentlyContinue
    if ($uvCommand) {
        & uv run --frozen agent.py
    } elseif (Test-Path '../.tools/bin/uv.exe') {
        & '../.tools/bin/uv.exe' run --frozen --cache-dir ../.uv-cache agent.py
    } else {
        throw 'Install uv first: https://docs.astral.sh/uv/getting-started/installation/'
    }
    $agentExitCode = $LASTEXITCODE
} finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($keyPointer)
    Remove-Item Env:GEMINI_API_KEY -ErrorAction SilentlyContinue
    $env:GEMINI_MODEL = $previousModel
}
exit $agentExitCode
