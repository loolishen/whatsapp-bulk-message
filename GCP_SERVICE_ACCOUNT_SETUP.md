# 🔐 GCP Service Account Setup for CI/CD

## Step 1: Create Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **IAM & Admin** → **Service Accounts**
3. Click **Create Service Account**
4. Fill in:
   - **Name**: `github-actions-deploy`
   - **Description**: `Service account for GitHub Actions deployment`
5. Click **Create and Continue**

## Step 2: Assign Roles

Assign these roles to the service account:
- **App Engine Admin**
- **Cloud Build Editor**
- **Storage Admin**
- **Cloud SQL Admin**
- **Secret Manager Secret Accessor**

## Step 3: Create and Download Key

1. Click on the service account you just created
2. Go to **Keys** tab
3. Click **Add Key** → **Create new key**
4. Choose **JSON** format
5. Download the key file

## Step 4: Add to GitHub Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `GCP_SA_KEY`
5. Value: Copy the entire contents of the downloaded JSON file
6. Click **Add secret**

## Step 5: Enable Cloud Build API

```bash
gcloud services enable cloudbuild.googleapis.com
```

## Step 6: Set Up Cloud Build Trigger (Optional)

1. Go to **Cloud Build** → **Triggers**
2. Click **Create Trigger**
3. Connect your GitHub repository
4. Choose **Push to a branch**
5. Branch: `main` or `master`
6. Build configuration: **Cloud Build configuration file (yaml)**
7. Location: `/cloudbuild.yaml`
8. Click **Create**

## Step 7: Test the Setup

1. Make a small change to your code
2. Commit and push to GitHub
3. Check the **Actions** tab in GitHub to see the deployment
4. Check **Cloud Build** in GCP Console to see the build logs

## Troubleshooting

### Common Issues:

**Issue: Permission denied**
- Make sure the service account has the correct roles
- Check that the JSON key is properly added to GitHub secrets

**Issue: Build fails**
- Check the Cloud Build logs
- Verify all environment variables are set correctly
- Make sure the app.yaml file is in the root directory

**Issue: Deployment fails**
- Check App Engine logs
- Verify the project ID is correct
- Make sure all required APIs are enabled

## Security Best Practices

1. **Rotate keys regularly** - Update the service account key every 90 days
2. **Use least privilege** - Only assign necessary roles
3. **Monitor usage** - Check Cloud Build and App Engine logs regularly
4. **Use Secret Manager** - Store sensitive data in Secret Manager instead of environment variables

## Commands for Manual Deployment

```bash
# Deploy to App Engine
gcloud app deploy

# Deploy specific version
gcloud app deploy --version=1-0-0

# Set traffic to new version
gcloud app services set-traffic default --splits=1-0-0=1

# View logs
gcloud app logs tail -s default

# List versions
gcloud app versions list
```
