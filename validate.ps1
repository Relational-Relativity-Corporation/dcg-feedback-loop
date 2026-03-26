# ================================================================
# validate.ps1 — DCG Feedback Loop validation
# ================================================================

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "============================================================"
Write-Host "DCG Feedback Loop - Validation"
Write-Host "============================================================"
Write-Host ""

Write-Host "[1/4] Divergence demo (delayed feedback)" -ForegroundColor Yellow
python -m solver.divergence_demo
Write-Host ""

Write-Host "[2/4] Delay comparison" -ForegroundColor Yellow
python -m solver.delay_comparison
Write-Host ""

Write-Host "[3/4] Guarded solver demo" -ForegroundColor Yellow
python -m metatron.guarded_solver
Write-Host ""

Write-Host "[4/4] Test suite (pytest)" -ForegroundColor Yellow
Write-Host "------------------------------------------------------------"
pytest tests/ -v

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host "ALL VALIDATIONS PASSED" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Red
    Write-Host "VALIDATION FAILED" -ForegroundColor Red
    Write-Host "============================================================" -ForegroundColor Red
    exit 1
}