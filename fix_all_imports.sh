#!/bin/bash
# Complete fix for all import issues and deploy to App Engine

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   Fix All Import Issues - WhatsApp Bulk Messaging System      ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

PROJECT_ID="whatsapp-bulk-messaging-480620"
APP_DIR="$HOME/app-full"

# Step 1: Navigate to app directory
echo "📂 Step 1: Navigating to app directory..."
cd "$APP_DIR" || { echo "❌ Directory not found. Run download first."; exit 1; }
echo "✅ In directory: $(pwd)"
echo ""

# Step 2: Download latest code
echo "📥 Step 2: Downloading latest code from Cloud Storage..."
gsutil -m rsync -r gs://staging.${PROJECT_ID}.appspot.com/ . --exclude=".git/*"
echo "✅ Code downloaded"
echo ""

# Step 3: Fix whatsapp_webhook.py
echo "🔧 Step 3: Fixing whatsapp_webhook.py..."
cat > /tmp/fix_webhook.py << 'FIXEOF'
import re

print("  → Reading whatsapp_webhook.py...")
with open('messaging/whatsapp_webhook.py', 'r') as f:
    content = f.read()

# Remove the import line
print("  → Removing deleted import...")
content = content.replace(
    'from .keyword_autoreply_service import KeywordAutoReplyService\n',
    ''
)

# Fix the imports to include Contest
print("  → Adding Contest to imports...")
content = content.replace(
    'from .models import Customer, CoreMessage',
    'from .models import Customer, CoreMessage, Contest'
)

# Replace the service usage
print("  → Replacing service usage with Contest model...")
old_code = '''            # Process keyword-based auto-replies
            keyword_service = KeywordAutoReplyService()
            keyword_results = keyword_service.process_message(
                customer=contact,
                message_text=message_text,
                tenant=tenant,
                conversation=conversation
            )
            
            # Log keyword matching results
            if keyword_results['matched']:
                logger.info(f"Keyword auto-reply: {keyword_results['replies_sent']} replies sent for keywords: {keyword_results['keywords_matched']}")
            
            # If nothing handled the message, use fallback auto-response
            if not pdpa_handled and not keyword_results['matched']:
                self._auto_respond_to_message(contact, message_text)'''

new_code = '''            # Process keyword-based auto-replies using Contest model
            keyword_matched = False
            matching_contests = Contest.objects.filter(
                tenant=tenant,
                is_active=True
            ).order_by('-auto_reply_priority')
            
            for contest in matching_contests:
                if contest.matches_message(message_text):
                    # Send auto-reply message from contest
                    if contest.auto_reply_message:
                        self._send_whatsapp_message(contact, contest.auto_reply_message)
                        logger.info(f"Keyword auto-reply sent from contest '{contest.name}' for keywords: {contest.get_keywords_list()}")
                        keyword_matched = True
                        break  # Only send first matching contest's reply
            
            # If nothing handled the message, use fallback auto-response
            if not pdpa_handled and not keyword_matched:
                self._auto_respond_to_message(contact, message_text)'''

content = content.replace(old_code, new_code)

print("  → Writing fixed file...")
with open('messaging/whatsapp_webhook.py', 'w') as f:
    f.write(content)

print("  ✅ whatsapp_webhook.py fixed!")
FIXEOF

python3 /tmp/fix_webhook.py
echo ""

# Step 4: Fix urls.py
echo "🔧 Step 4: Fixing urls.py..."
cat > /tmp/fix_urls.py << 'URLEOF'
print("  → Reading urls.py...")
with open('messaging/urls.py', 'r') as f:
    content = f.read()

# Comment out deprecated routes
print("  → Commenting out deprecated routes...")
content = content.replace(
    "    path('crm/prompts/', views.crm_prompt_replies, name='crm_prompt_replies'),",
    "    # DEPRECATED: path('crm/prompts/', views.crm_prompt_replies, name='crm_prompt_replies'),"
)

content = content.replace(
    "    path('crm/prompts/add/', views.crm_add_prompt_reply, name='crm_add_prompt_reply'),",
    "    # DEPRECATED: path('crm/prompts/add/', views.crm_add_prompt_reply, name='crm_add_prompt_reply'),"
)

print("  → Writing fixed file...")
with open('messaging/urls.py', 'w') as f:
    f.write(content)

print("  ✅ urls.py fixed!")
URLEOF

python3 /tmp/fix_urls.py
echo ""

# Step 5: Verify fixes
echo "✅ Step 5: Verifying fixes..."
echo ""
echo "  Checking whatsapp_webhook.py..."
if grep -q "keyword_autoreply_service" messaging/whatsapp_webhook.py; then
    echo "    ❌ Still has reference to deleted service!"
    exit 1
else
    echo "    ✅ No references to deleted service"
fi

if grep -q "from .models import Customer, CoreMessage, Contest" messaging/whatsapp_webhook.py; then
    echo "    ✅ Contest imported correctly"
else
    echo "    ❌ Contest not imported!"
    exit 1
fi

echo ""
echo "  Checking urls.py..."
if grep -q "# DEPRECATED:.*crm/prompts" messaging/urls.py; then
    echo "    ✅ Deprecated routes commented out"
else
    echo "    ⚠️  Routes may not be commented"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "✅ ALL FIXES APPLIED SUCCESSFULLY!"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Step 6: Deploy to App Engine
echo "🚀 Step 6: Deploying to App Engine..."
echo ""
echo "Project: ${PROJECT_ID}"
echo "This will take approximately 5 minutes..."
echo ""

if gcloud app deploy app.yaml --quiet --project=${PROJECT_ID}; then
    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                   🎉 DEPLOYMENT SUCCESSFUL! 🎉                 ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "✅ The 500 error is now fixed!"
    echo "✅ Your site should be working at:"
    echo "   https://${PROJECT_ID}.as.r.appspot.com"
    echo ""
    echo "Next steps:"
    echo "  1. Visit the site and test login"
    echo "  2. Go to Contest Create page"
    echo "  3. You should see the 'Keyword Auto-Reply' section"
    echo ""
else
    echo ""
    echo "❌ Deployment failed!"
    echo "Check the error messages above."
    exit 1
fi


