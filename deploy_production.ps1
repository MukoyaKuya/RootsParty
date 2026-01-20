#!/usr/bin/env pwsh
# RootsParty Production Deployment Script
# This script guides you through the deployment process step-by-step

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RootsParty Production Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$PROJECT_ID = "gen-lang-client-0549116861"  # Updated from gcloud config
$REGION = "europe-north1"
$SERVICE_NAME = "roots-party"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/$SERVICE_NAME"

# Step 1: Check Prerequisites
Write-Host "[1/8] Checking Prerequisites..." -ForegroundColor Yellow
Write-Host ""

# Check if gcloud is installed
if (!(Get-Command gcloud -ErrorAction SilentlyContinue)) {
    Write-Host "❌ ERROR: gcloud CLI not found!" -ForegroundColor Red
    Write-Host "Install from: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

# Check if Docker is installed
if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ ERROR: Docker not found!" -ForegroundColor Red
    Write-Host "Install from: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Prerequisites OK" -ForegroundColor Green
Write-Host ""

# Step 2: Generate Secrets
Write-Host "[2/8] Generating Production Secrets..." -ForegroundColor Yellow
Write-Host ""

$SECRET_KEY = $env:SECRET_KEY
if (-not $SECRET_KEY) {
    Write-Host "⚠️ SECRET_KEY not found in environment" -ForegroundColor Yellow
}
Write-Host ""

# Step 3: Database Credentials (Configured)
Write-Host "[3/8] Database Credentials" -ForegroundColor Yellow
$DATABASE_URL = $env:DATABASE_URL
if (-not $DATABASE_URL) {
    Write-Host "⚠️ DATABASE_URL not found in environment" -ForegroundColor Yellow
}
Write-Host ""


# Step 4: Environment Variables
Write-Host "[4/8] Configuring Environment Variables..." -ForegroundColor Yellow
Write-Host ""

$ALLOWED_HOSTS = "*"
Write-Host "✅ Using universal host: $ALLOWED_HOSTS" -ForegroundColor Green

$GS_BUCKET_NAME = ""
Write-Host "✅ Using local storage for media (no GCS bucket specified)" -ForegroundColor Yellow

Write-Host ""
Write-Host "✅ Environment variables configured" -ForegroundColor Green
Write-Host ""

# Step 5: Build Docker Image
Write-Host "[5/8] Building Docker Image..." -ForegroundColor Yellow
Write-Host ""

Write-Host "Building: $IMAGE_NAME" -ForegroundColor Cyan
docker build -t "${IMAGE_NAME}:latest" .

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ ERROR: Docker build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Docker image built successfully" -ForegroundColor Green
Write-Host ""

# Step 6: Push to Google Container Registry
Write-Host "[6/8] Pushing to Google Container Registry..." -ForegroundColor Yellow
Write-Host ""

Write-Host "Configuring Docker for GCR..." -ForegroundColor Cyan
gcloud auth configure-docker

Write-Host "Pushing image..." -ForegroundColor Cyan
docker push "${IMAGE_NAME}:latest"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ ERROR: Docker push failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Image pushed to GCR" -ForegroundColor Green
Write-Host ""

# Step 7: Deploy to Cloud Run
Write-Host "[7/8] Deploying to Cloud Run..." -ForegroundColor Yellow
Write-Host ""

Write-Host "Deploying service..." -ForegroundColor Cyan
gcloud run deploy $SERVICE_NAME `
    --image "${IMAGE_NAME}:latest" `
    --platform managed `
    --region $REGION `
    --allow-unauthenticated `
    --memory 512Mi `
    --cpu 1 `
    --max-instances 10 `
    --timeout 300

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ ERROR: Cloud Run deployment failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Deployed to Cloud Run" -ForegroundColor Green
Write-Host ""

# Step 8: Verify Deployment
Write-Host "[8/8] Verifying Deployment..." -ForegroundColor Yellow
Write-Host ""

$SERVICE_URL = gcloud run services describe $SERVICE_NAME --region $REGION --format "value(status.url)"

Write-Host "Service URL: $SERVICE_URL" -ForegroundColor Cyan
Write-Host ""

Write-Host "Testing security headers..." -ForegroundColor Cyan
curl -I $SERVICE_URL

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Service URL: $SERVICE_URL" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Verify security headers are present" -ForegroundColor White
Write-Host "2. Test the application functionality" -ForegroundColor White
Write-Host "3. Run database migrations if needed" -ForegroundColor White
Write-Host "4. Create superuser account" -ForegroundColor White
Write-Host "5. Monitor logs for any issues" -ForegroundColor White
Write-Host ""
Write-Host "View logs:" -ForegroundColor Yellow
Write-Host "  gcloud run services logs tail $SERVICE_NAME --region $REGION" -ForegroundColor Gray
Write-Host ""
