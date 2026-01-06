# PowerShell script to upload CSV files to Google Cloud Storage
# The brackets in filenames cause issues, so we'll copy them with simpler names first

Write-Host "📤 Uploading CSV files to Google Cloud Storage..." -ForegroundColor Cyan
Write-Host ""

# Get current directory
$currentDir = Get-Location

# File paths
$file1 = Join-Path $currentDir "[WIP] KHIND Merdeka Campaign 2025_W1 Submissions - CU Edited_export_options.csv"
$file2 = Join-Path $currentDir "[WIP] KHIND Merdeka Campaign 2025_W2 Submissions - CU_Edited submissions.csv"

# Check if files exist
if (-not (Test-Path $file1)) {
    Write-Host "❌ File 1 not found: $file1" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $file2)) {
    Write-Host "❌ File 2 not found: $file2" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Found both CSV files" -ForegroundColor Green
Write-Host ""

# Create temporary copies with simpler names (no brackets)
$temp1 = Join-Path $env:TEMP "W1_Submissions.csv"
$temp2 = Join-Path $env:TEMP "W2_Submissions.csv"

Write-Host "📋 Creating temporary copies..." -ForegroundColor Yellow
Copy-Item $file1 -Destination $temp1 -Force
Copy-Item $file2 -Destination $temp2 -Force

Write-Host "✅ Temporary files created" -ForegroundColor Green
Write-Host ""

# Upload with simpler names
Write-Host "📤 Uploading to Google Cloud Storage..." -ForegroundColor Yellow
gsutil cp $temp1 "gs://staging.whatsapp-bulk-messaging-480620.appspot.com/W1_Submissions.csv"
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ W1 CSV uploaded successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to upload W1 CSV" -ForegroundColor Red
}

gsutil cp $temp2 "gs://staging.whatsapp-bulk-messaging-480620.appspot.com/W2_Submissions.csv"
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ W2 CSV uploaded successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to upload W2 CSV" -ForegroundColor Red
}

# Clean up temp files
Write-Host ""
Write-Host "🧹 Cleaning up temporary files..." -ForegroundColor Yellow
Remove-Item $temp1 -Force -ErrorAction SilentlyContinue
Remove-Item $temp2 -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "✅ Done! CSV files uploaded to:" -ForegroundColor Green
Write-Host "   gs://staging.whatsapp-bulk-messaging-480620.appspot.com/W1_Submissions.csv"
Write-Host "   gs://staging.whatsapp-bulk-messaging-480620.appspot.com/W2_Submissions.csv"
Write-Host ""
Write-Host "⚠️  Note: The files are uploaded with simpler names." -ForegroundColor Yellow
Write-Host "   You'll need to update csv_data_service.py to look for these names,"
Write-Host "   OR rename them in Cloud Storage to match the original names."
Write-Host ""
Write-Host "💡 Better option: The app works WITHOUT CSV files!" -ForegroundColor Cyan
Write-Host "   Just deploy the fixed views.py and the contest manager will work."

