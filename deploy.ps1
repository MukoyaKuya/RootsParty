$PROJECT_ID = "gen-lang-client-0549116861"
$REGION = "europe-north1"
$APP_NAME = "roots-party"

Write-Host "Deploying $APP_NAME to Google Cloud Run ($REGION)..."

# Set Project
Write-Host "Setting project..."
gcloud config set project $PROJECT_ID

# Build Container
Write-Host "Building container image..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$APP_NAME .

# Deploy
Write-Host "Deploying to Cloud Run..."
gcloud run deploy $APP_NAME `
    --image gcr.io/$PROJECT_ID/$APP_NAME `
    --platform managed `
    --region $REGION `
    --allow-unauthenticated

Write-Host "Deployment Complete!"
