#!/bin/bash
# Upload CSV files to App Engine
# Run this in Cloud Shell after uploading files to GCS

set -e

echo "📤 Uploading CSV files to App Engine..."
echo "========================================"

cd ~/app-full

# Download CSV files from staging bucket
echo "📥 Downloading CSV files from staging..."
gsutil cp "gs://staging.whatsapp-bulk-messaging-480620.appspot.com/[WIP] KHIND Merdeka Campaign 2025_W1 Submissions - CU Edited_export_options.csv" . 2>/dev/null || echo "W1 CSV not in staging, will need to upload manually"
gsutil cp "gs://staging.whatsapp-bulk-messaging-480620.appspot.com/[WIP] KHIND Merdeka Campaign 2025_W2 Submissions - CU_Edited submissions.csv" . 2>/dev/null || echo "W2 CSV not in staging, will need to upload manually"

# Check if files exist
if [ -f "[WIP] KHIND Merdeka Campaign 2025_W1 Submissions - CU Edited_export_options.csv" ]; then
    echo "✅ W1 CSV found"
else
    echo "⚠️  W1 CSV not found - you'll need to upload it manually"
fi

if [ -f "[WIP] KHIND Merdeka Campaign 2025_W2 Submissions - CU_Edited submissions.csv" ]; then
    echo "✅ W2 CSV found"
else
    echo "⚠️  W2 CSV not found - you'll need to upload it manually"
fi

echo ""
echo "📋 To upload CSV files manually:"
echo "1. Upload them to Google Cloud Storage first:"
echo "   gsutil cp '[WIP] KHIND Merdeka Campaign 2025_W1 Submissions - CU Edited_export_options.csv' gs://staging.whatsapp-bulk-messaging-480620.appspot.com/"
echo "   gsutil cp '[WIP] KHIND Merdeka Campaign 2025_W2 Submissions - CU_Edited submissions.csv' gs://staging.whatsapp-bulk-messaging-480620.appspot.com/"
echo ""
echo "2. Then download them in Cloud Shell and they'll be included in deployment"
echo ""
echo "Note: The app will work WITHOUT CSV files - it will just show empty Merdeka contests"

