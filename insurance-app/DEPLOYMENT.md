# Deployment Guide - Cymbal Auto Insurance App

This guide explains how to deploy the Cymbal Auto Insurance application to Google Cloud Run, with the backend (WebSocket server) and frontend (React app) as separate Cloud Run services.

## Architecture

```
┌─────────────────────┐
│  Frontend (React)   │
│  Cloud Run Service  │  ──────┐
│  Port: 80           │        │
│  Public URL         │        │ WebSocket
└─────────────────────┘        │ Connection
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Backend (Python)   │
                    │  Cloud Run Service  │
                    │  Port: 8765         │
                    │  WebSocket Server   │
                    │  Gemini Live API    │
                    └─────────────────────┘
```

## Prerequisites

1. **Google Cloud Project**
   - Project ID: `general-ak` (or your project)
   - Billing enabled
   - APIs enabled:
     - Cloud Run API
     - Cloud Build API
     - Artifact Registry API
     - Vertex AI API

2. **Local Tools**
   - Google Cloud SDK (gcloud)
   - Git
   - Docker (optional, for local testing)

3. **Authentication**
   ```bash
   gcloud auth login
   gcloud config set project general-ak
   gcloud auth application-default login
   ```

## Deployment Steps

### Step 1: Deploy Backend (WebSocket Server)

The backend must be deployed first because the frontend needs its URL.

```bash
# Navigate to backend directory
cd insurance-app/backend

# Submit build to Cloud Build
gcloud builds submit \
  --config=cloudbuild.yaml \
  --region=us-central1

# This will:
# 1. Create Artifact Registry repository (if needed)
# 2. Build Docker image
# 3. Push to Artifact Registry
# 4. Deploy to Cloud Run as 'cymbal-auto-backend'
```

**Expected Output:**
```
Service [cymbal-auto-backend] revision [cymbal-auto-backend-00001-xxx] has been deployed
Service URL: https://cymbal-auto-backend-xxxxxxxxxx-uc.a.run.app
```

**Save the backend URL** - you'll need it for the frontend.

### Step 2: Deploy Frontend (React App)

The frontend deployment will automatically fetch the backend URL and configure the WebSocket connection.

```bash
# Navigate to app root directory
cd insurance-app

# Submit build to Cloud Build
gcloud builds submit \
  --config=cloudbuild.yaml \
  --region=us-central1

# This will:
# 1. Get backend Cloud Run URL
# 2. Convert to WebSocket URL (wss://)
# 3. Build React app with backend URL
# 4. Deploy to Cloud Run as 'cymbal-auto-frontend'
```

**Expected Output:**
```
Service [cymbal-auto-frontend] revision [cymbal-auto-frontend-00001-xxx] has been deployed
Service URL: https://cymbal-auto-frontend-xxxxxxxxxx-uc.a.run.app
```

### Step 3: Test the Deployment

1. **Open the frontend URL** in your browser
2. **Click "Start Claim"** button
3. **Grant camera/microphone permissions**
4. **Test the AI assistant** by showing damage and speaking

## Manual Deployment (Alternative)

If you prefer to deploy manually without Cloud Build:

### Backend Manual Deployment

```bash
cd insurance-app/backend

# Build Docker image
docker build -t cymbal-auto-backend .

# Tag for Artifact Registry
docker tag cymbal-auto-backend \
  us-central1-docker.pkg.dev/general-ak/cymbal-auto-insurance/insurance-backend:latest

# Push to Artifact Registry
docker push us-central1-docker.pkg.dev/general-ak/cymbal-auto-insurance/insurance-backend:latest

# Deploy to Cloud Run
gcloud run deploy cymbal-auto-backend \
  --image=us-central1-docker.pkg.dev/general-ak/cymbal-auto-insurance/insurance-backend:latest \
  --region=us-central1 \
  --platform=managed \
  --port=8080 \
  --allow-unauthenticated \
  --memory=2Gi \
  --cpu=2 \
  --min-instances=0 \
  --max-instances=10 \
  --session-affinity \
  --execution-environment=gen2 \
  --set-env-vars=GOOGLE_CLOUD_PROJECT=general-ak,GOOGLE_CLOUD_LOCATION=us-central1,GEMINI_MODEL=gemini-live-2.5-flash-preview-native-audio-09-2025
```

### Frontend Manual Deployment

```bash
cd insurance-app

# Get backend URL
BACKEND_URL=$(gcloud run services describe cymbal-auto-backend \
  --region=us-central1 \
  --format='value(status.url)')

# Convert to WebSocket URL
WS_URL=$(echo $BACKEND_URL | sed 's/https:/wss:/')

# Build Docker image with backend URL
docker build \
  --build-arg REACT_APP_WS_URL=$WS_URL \
  -t cymbal-auto-frontend .

# Tag for Artifact Registry
docker tag cymbal-auto-frontend \
  us-central1-docker.pkg.dev/general-ak/cymbal-auto-insurance/insurance-frontend:latest

# Push to Artifact Registry
docker push us-central1-docker.pkg.dev/general-ak/cymbal-auto-insurance/insurance-frontend:latest

# Deploy to Cloud Run
gcloud run deploy cymbal-auto-frontend \
  --image=us-central1-docker.pkg.dev/general-ak/cymbal-auto-insurance/insurance-frontend:latest \
  --region=us-central1 \
  --platform=managed \
  --port=80 \
  --allow-unauthenticated \
  --memory=512Mi \
  --cpu=1
```

## Configuration

### Backend Environment Variables

Set via Cloud Run:

```bash
gcloud run services update cymbal-auto-backend \
  --region=us-central1 \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=general-ak,GOOGLE_CLOUD_LOCATION=us-central1,GEMINI_MODEL=gemini-live-2.5-flash-preview-native-audio-09-2025,WEBSOCKET_PORT=8080"
```

### Frontend Environment Variables

The frontend WebSocket URL is baked into the build. To update:

1. Rebuild frontend with new backend URL
2. Or modify the React code to use a runtime configuration

## Monitoring and Logs

### View Logs

**Backend logs:**
```bash
gcloud run services logs read cymbal-auto-backend \
  --region=us-central1 \
  --limit=50
```

**Frontend logs:**
```bash
gcloud run services logs read cymbal-auto-frontend \
  --region=us-central1 \
  --limit=50
```

### Cloud Console

- **Cloud Run Console**: https://console.cloud.google.com/run
- **Cloud Build History**: https://console.cloud.google.com/cloud-build/builds
- **Artifact Registry**: https://console.cloud.google.com/artifacts

## Troubleshooting

### Backend Issues

**WebSocket connection fails:**
```bash
# Check backend is running
gcloud run services describe cymbal-auto-backend --region=us-central1

# Check logs for errors
gcloud run services logs read cymbal-auto-backend --region=us-central1

# Test WebSocket endpoint
wscat -c wss://cymbal-auto-backend-xxx.run.app
```

**Gemini API errors:**
```bash
# Verify Vertex AI is enabled
gcloud services enable aiplatform.googleapis.com

# Check service account permissions
gcloud run services get-iam-policy cymbal-auto-backend --region=us-central1
```

### Frontend Issues

**Cannot connect to backend:**
- Check frontend build logs for correct WebSocket URL
- Verify backend service is deployed and running
- Check browser console for WebSocket errors

**Camera/Microphone not working:**
- Ensure HTTPS is used (Cloud Run provides this)
- Check browser permissions
- Test on different browsers

### Build Failures

**Artifact Registry errors:**
```bash
# Create repository manually
gcloud artifacts repositories create cymbal-auto-insurance \
  --repository-format=docker \
  --location=us-central1 \
  --description="Cymbal Auto Insurance App"
```

**Permission errors:**
```bash
# Grant Cloud Build service account permissions
PROJECT_NUMBER=$(gcloud projects describe general-ak --format='value(projectNumber)')

gcloud projects add-iam-policy-binding general-ak \
  --member=serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com \
  --role=roles/run.admin

gcloud projects add-iam-policy-binding general-ak \
  --member=serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com \
  --role=roles/iam.serviceAccountUser
```

## Scaling Configuration

### Backend Scaling

```bash
gcloud run services update cymbal-auto-backend \
  --region=us-central1 \
  --min-instances=1 \
  --max-instances=20 \
  --concurrency=80
```

### Frontend Scaling

```bash
gcloud run services update cymbal-auto-frontend \
  --region=us-central1 \
  --min-instances=0 \
  --max-instances=10 \
  --concurrency=100
```

## Cost Optimization

### Development/Testing
- Set `--min-instances=0` for both services
- Use smaller machine types
- Enable request-based scaling

### Production
- Set `--min-instances=1` for backend (faster cold starts)
- Increase concurrency for better utilization
- Monitor usage and adjust accordingly

## Security Considerations

### Production Checklist

- [ ] Enable authentication if not public
- [ ] Configure CORS properly
- [ ] Add rate limiting
- [ ] Set up monitoring and alerts
- [ ] Configure Cloud Armor (WAF)
- [ ] Use Secret Manager for sensitive data
- [ ] Enable VPC for backend
- [ ] Implement request validation

### Enable Authentication

```bash
# Remove --allow-unauthenticated flag during deployment
gcloud run services update cymbal-auto-backend \
  --region=us-central1 \
  --no-allow-unauthenticated
```

## Continuous Deployment

### Set up Cloud Build Triggers

1. **Go to Cloud Build Triggers**: https://console.cloud.google.com/cloud-build/triggers
2. **Create trigger for backend**:
   - Event: Push to branch
   - Repository: Your repo
   - Branch: `^main$`
   - Build configuration: `/insurance-app/backend/cloudbuild.yaml`

3. **Create trigger for frontend**:
   - Event: Push to branch
   - Repository: Your repo
   - Branch: `^main$`
   - Build configuration: `/insurance-app/cloudbuild.yaml`

## URLs

After deployment, you'll have two services:

- **Frontend**: `https://cymbal-auto-frontend-[hash]-uc.a.run.app`
- **Backend**: `wss://cymbal-auto-backend-[hash]-uc.a.run.app`

## Clean Up

To delete all resources:

```bash
# Delete Cloud Run services
gcloud run services delete cymbal-auto-backend --region=us-central1 --quiet
gcloud run services delete cymbal-auto-frontend --region=us-central1 --quiet

# Delete Artifact Registry images
gcloud artifacts docker images delete \
  us-central1-docker.pkg.dev/general-ak/cymbal-auto-insurance/insurance-backend:latest \
  --quiet

gcloud artifacts docker images delete \
  us-central1-docker.pkg.dev/general-ak/cymbal-auto-insurance/insurance-frontend:latest \
  --quiet

# Delete repository (optional)
gcloud artifacts repositories delete cymbal-auto-insurance \
  --location=us-central1 \
  --quiet
```

## Support

For issues or questions:
- Check Cloud Run logs
- Review Cloud Build history
- Check Vertex AI quota and limits
- Review Gemini Live API documentation

---

**Note**: This deployment guide assumes you're using the `general-ak` project. Adjust project IDs and regions as needed for your environment.
