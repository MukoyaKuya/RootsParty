#!/usr/bin/env pwsh
# Run Django migrations on production Cloud Run database

$PROJECT_ID = "gen-lang-client-0549116861"
$REGION = "europe-north1"
$SERVICE_NAME = "roots-party"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Running Production Migrations" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set project
gcloud config set project $PROJECT_ID

# Create a temporary Cloud Run job to run migrations
Write-Host "Creating migration job..." -ForegroundColor Yellow

# Use gcloud run jobs to execute migrations
gcloud run jobs create migrate-roots-party `
    --image "europe-north1-docker.pkg.dev/$PROJECT_ID/cloud-run-source-deploy/$SERVICE_NAME:latest" `
    --region $REGION `
    --command python `
    --args manage.py,migrate `
    --set-env-vars="DATABASE_URL=$env:DATABASE_URL,SECRET_KEY=$env:SECRET_KEY,ALLOWED_HOSTS=*" `
    --max-retries 1 `
    --task-timeout 300 `
    2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Migration job created" -ForegroundColor Green
    Write-Host ""
    Write-Host "Executing migration job..." -ForegroundColor Yellow
    gcloud run jobs execute migrate-roots-party --region $REGION --wait
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Migrations completed successfully!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "❌ Migration execution failed" -ForegroundColor Red
        Write-Host "Check logs: gcloud run jobs executions logs read migrate-roots-party --region $REGION" -ForegroundColor Yellow
    }
} else {
    Write-Host "Job may already exist. Executing existing job..." -ForegroundColor Yellow
    gcloud run jobs execute migrate-roots-party --region $REGION --wait
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Migration Process Complete" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
