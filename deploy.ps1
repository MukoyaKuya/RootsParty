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
    --allow-unauthenticated `
    --set-env-vars "DEBUG=False" `
    --set-env-vars "CSRF_TRUSTED_ORIGINS=https://roots-party-1073897174388.europe-north1.run.app" `
    --set-env-vars "DATABASE_URL=postgresql://neondb_owner:npg_aPjBTZvw8cD2@ep-autumn-math-ahlr3cf2-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

Write-Host "Deployment Complete!"
