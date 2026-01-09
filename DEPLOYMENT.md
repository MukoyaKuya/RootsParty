# Roots Party Deployment Guide

This guide explains how to deploy the Roots Party application to Google Cloud Run.

## Prerequisites

- **Google Cloud SDK** installed and authenticated (`gcloud auth login`).
- **Docker** installed and running (for building the container image).
- **PowerShell** (for running the deployment script).

## Deployment Script

The project includes a `deploy.ps1` script that automates the deployment process.

### Steps to Deploy

1.  **Open PowerShell**: Open a terminal or PowerShell credentials in the project root directory.
2.  **Run the Script**: Execute the following command:
    ```powershell
    .\deploy.ps1
    ```
    _Note: If you encounter execution policy errors, you may need to run `powershell -ExecutionPolicy Bypass -File deploy.ps1`._

### What the Script Does

1.  **Sets Project**: Configures `gcloud` to use the project ID `gen-lang-client-0549116861`.
2.  **Builds Container**:Submits a build to Google Cloud Build, which creates a Docker image and stores it in the Container Registry (`gcr.io`).
3.  **Deploys to Cloud Run**: Deploys the new image to the Cloud Run service named `roots-party`. It sets necessary environment variables like `DEBUG=False`, `CSRF_TRUSTED_ORIGINS`, and `DATABASE_URL`.

## Verification

After the script completes, it will output the **Service URL**. You can visit this URL to see your live application.

Current URL: [https://roots-party-1073897174388.europe-north1.run.app](https://roots-party-1073897174388.europe-north1.run.app)
