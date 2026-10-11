# AWS Tier 1 Deployment Guide — Hindon River Sentinel

> **Architecture:** AWS App Runner (Backend) + Amazon S3 & CloudFront (Frontend)  
> **Estimated Cost:** ~$10 - $25 / month (Eligible for AWS Free Tier)  
> **Estimated Deployment Time:** 15 - 25 minutes  

---

## 1. Architecture Overview

```
 [ Citizens / District Admin ]
               │
               ▼
   [ Amazon CloudFront CDN ] (HTTPS / SSL)
       │              │
       │ /*           │ /api/*
       ▼              ▼
 [ Amazon S3 ]   [ AWS App Runner ]
 (React SPA)     (FastAPI Python Container)
                      │
                      ▼
               [ hindon_river.db ]
```

* **Frontend:** Compiled React + Vite static assets hosted on **Amazon S3**, distributed globally via **CloudFront** CDN with HTTPS.
* **Backend:** Dockerized FastAPI multi-agent backend running on **AWS App Runner** (fully managed container runner, auto-TLS, health checks, automatic scaling).
* **Database & Persistence:** Thread-safe SQLite / in-memory database with pre-seeded Hindon river GIS data (can optionally be upgraded to RDS PostgreSQL later).

---

## 2. Prerequisites

1. **AWS CLI** installed and configured (`aws configure` with an IAM user having Admin/PowerUser permissions).
2. **Docker** installed locally (to build and push the backend container to ECR).
3. **Node.js 18+** & npm.

---

## 3. Step 1: Deploy Backend to AWS App Runner

### Option A: Via Amazon ECR & AWS App Runner (Recommended)

#### 1. Create an ECR Private Repository:
```bash
aws ecr create-repository \
  --repository-name hindon-river-backend \
  --region us-east-1
```
*(Take note of your repository URI, e.g., `<ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/hindon-river-backend`)*

#### 2. Authenticate Docker with ECR:
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com
```

#### 3. Build & Push the Docker Image:
```bash
cd backend

# Build image
docker build -t hindon-river-backend:latest .

# Tag for ECR
docker tag hindon-river-backend:latest <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/hindon-river-backend:latest

# Push to ECR
docker push <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/hindon-river-backend:latest

cd ..
```

#### 4. Create App Runner Service:
You can create this via the AWS Console in 2 minutes:
1. Open the [AWS App Runner Console](https://console.aws.amazon.com/apprunner).
2. Click **Create service**.
3. **Source**: Select **Container registry** -> **Amazon ECR**.
4. Browse and select your `hindon-river-backend` repository and tag `latest`.
5. **Deployment settings**: Select **Automatic** (so new pushes trigger redeploy).
6. **ECR access role**: Click **Create new service role** (AppRunnerECRAccessRole).
7. **Service settings**:
   * Service name: `hindon-river-sentinel-api`
   * Port: `8000`
   * vCPU: `1 vCPU`, Memory: `2 GB`
   * Health check path: `/api/health`
8. Click **Next** -> **Create & Deploy**.

Once deployed (3-4 minutes), AWS App Runner will provide your default HTTPS URL:
`https://<apprunner-id>.us-east-1.awsapprunner.com`

Test it:
```bash
curl https://<apprunner-id>.us-east-1.awsapprunner.com/api/health
```

---

## 4. Step 2: Deploy Frontend to Amazon S3 & CloudFront

### 1. Create S3 Bucket for Static Hosting
```bash
# S3 bucket names must be globally unique
BUCKET_NAME="hindon-river-sentinel-ui-$(aws sts get-caller-identity --query Account --output text)"

aws s3 mb s3://$BUCKET_NAME --region us-east-1
```

### 2. Build Frontend with Production Backend URL
Set the environment variable `VITE_API_BASE_URL` to point to your App Runner API:
```bash
cd frontend

# Set backend URL (or keep /api if routing through CloudFront)
export VITE_API_BASE_URL="https://<apprunner-id>.us-east-1.awsapprunner.com/api"

# Build production assets
npm run build

# Upload to S3
aws s3 sync dist/ s3://$BUCKET_NAME --delete

cd ..
```

### 3. Create Amazon CloudFront Distribution

In AWS Console:
1. Go to **CloudFront** -> **Create distribution**.
2. **Origin domain**: Select your S3 bucket `$BUCKET_NAME`.
3. **Origin access**: Select **Origin access control settings (recommended)** -> click **Create new OAC**.
4. **Viewer protocol policy**: Select **Redirect HTTP to HTTPS**.
5. **Default root object**: Set to `index.html`.
6. Under **Custom error responses**:
   * Click **Add error response**.
   * HTTP error code: `403: Forbidden` (and `404: Not Found`).
   * Response page path: `/index.html`.
   * HTTP response code: `200: OK` (This enables React SPA client routing).
7. Click **Create distribution**.
8. Copy the recommended S3 Bucket Policy from CloudFront and apply it to your S3 bucket permissions.

Your frontend is now live at:
`https://<cloudfront-id>.cloudfront.net`

---

## 5. Alternative 1-Click Frontend Deployment: AWS Amplify Hosting

If you want automated GitHub CI/CD for the frontend without manual S3/CloudFront setups:
1. Push your repository to GitHub.
2. Go to **AWS Amplify Console** -> **Create new app** -> **Host web app**.
3. Connect your GitHub repository and select branch `main`.
4. Set App root to `frontend`.
5. Under **Environment variables**, add:
   * Key: `VITE_API_BASE_URL`
   * Value: `https://<apprunner-id>.us-east-1.awsapprunner.com/api`
6. Click **Save and deploy**. Amplify will build and deploy your React app automatically with SSL included.

---

## 6. Verification Checklist

- [ ] Health check: `curl https://<apprunner-id>.us-east-1.awsapprunner.com/api/health` returns status `healthy`.
- [ ] UI load: Visit your CloudFront / Amplify URL; ensure dark-theme command dashboard renders smoothly.
- [ ] Map tiles: Open **Command Map**; verify dark OpenStreetMap basemap loads without any watermarks.
- [ ] Live demo scenario: Click **Live Demo Replay** -> Run automated triage, source tracking, and dispatching.
- [ ] Executive Briefing: Navigate to **IAS Executive Briefing** tab; verify Hindi and English dossier generation.
