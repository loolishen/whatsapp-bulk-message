# Multi-Step Conversation Flow System

## 🎯 Overview

The Multi-Step Conversation Flow System allows you to create step-by-step conversational experiences for your WhatsApp contests. Instead of a single keyword-reply, you can now guide users through multiple steps, collecting information progressively.

## 🌟 Key Features

- **Sequential Conversation Steps**: Create ordered steps (Step 1, 2, 3, etc.)
- **Keyword-Based Triggers**: Each step has its own set of keywords
- **Auto-Advancement**: Automatically progress users through steps
- **Progress Tracking**: Track where each user is in the conversation
- **Flexible Design**: Works alongside traditional single-step auto-replies

## 📋 How It Works

### 1. **Contest Creation**

When creating a contest, you'll see a new "Conversation Flow" section that replaces the simple keyword auto-reply:

- **Step 1 (Required)**: The initial contact step - triggers when users first reach out
- **Additional Steps (Optional)**: Add as many steps as needed for your flow

Each step includes:
- **Step Name**: Descriptive name (e.g., "Welcome", "Request NRIC")
- **Keywords**: Comma-separated keywords that trigger this step
- **Auto-Reply Message**: The message sent when keywords match

### 2. **User Experience**

Example conversation flow:

```
📱 User: "JOIN"
🤖 Bot: "🎉 Welcome! To enter, please send a photo of your receipt..."

📱 User: "PHOTO" [sends image]
🤖 Bot: "Great! Now please send your NRIC photo..."

📱 User: "NRIC" [sends image]
🤖 Bot: "Perfect! Your entry is complete. Good luck! 🍀"
```

### 3. **Progress Tracking**

The system automatically tracks:
- Which step each user is currently on
- When they started the conversation
- When they last interacted
- Whether they've completed the flow

## 🔧 Technical Implementation

### New Database Models

#### `ContestConversationStep`
Stores each step in a contest's conversation flow:
- `step_order`: Sequential order (1, 2, 3...)
- `step_name`: Descriptive name
- `keywords`: Comma-separated trigger keywords
- `auto_reply_message`: Response message
- `auto_advance_to_next`: Auto-progress to next step
- `wait_for_response`: Wait for user response before advancing

#### `UserConversationProgress`
Tracks user progress through conversations:
- `customer`: The user
- `contest`: Which contest
- `current_step`: Where they are in the flow
- `completed`: Whether they finished
- `started_at` / `last_interaction_at`: Timing info

### Service Layer

#### `ConversationFlowService`
Handles conversation logic:

```python
from messaging.conversation_flow_service import ConversationFlowService

service = ConversationFlowService()
result = service.process_message(
    customer=customer,
    message_text="JOIN",
    tenant=tenant,
    conversation=conversation
)

# Result contains:
# - matched: bool (did any step match?)
# - contest: Contest (which contest matched)
# - step: ContestConversationStep (which step matched)
# - reply_message: str (message to send)
# - advanced: bool (did user advance to next step?)
# - completed: bool (is conversation done?)
```

### Integration with WhatsApp Webhook

The webhook automatically processes conversation flows:

1. **Priority Order**: Conversation flows are checked FIRST
2. **Step Matching**: Current step's keywords are matched against message
3. **Auto-Reply**: Appropriate message is sent
4. **Advancement**: User is moved to next step (if configured)
5. **Fallback**: Simple keyword matching for contests without flows

## 📝 Creating a Conversation Flow Contest

### Example: Receipt Contest with Multi-Step Flow

**Step 1: Welcome**
- Keywords: `JOIN, START, HI, HELLO, MASUK, SERTAI`
- Message: "🎉 Welcome to our Khind Contest! To participate, please send PHOTO of your receipt with minimum RM98 purchase."

**Step 2: Receipt Verification**
- Keywords: `PHOTO, RECEIPT, IMAGE, GAMBAR, PIC`
- Message: "Excellent! Now please send your NRIC photo so we can verify your identity."

**Step 3: NRIC Verification**
- Keywords: `NRIC, IC, IDENTITY, KTP, ID`
- Message: "Perfect! ✅ Your entry is complete! Entry #12345\n\nWinner announcement: 31 Aug 2025\nGood luck! 🍀"

### Step 4: Advanced Usage

You can also:
- **Reset Progress**: Clear a user's conversation state
- **Check Status**: See where a user is in the flow
- **Handle Branching**: Create conditional flows based on responses

## 🚀 Deployment

### Quick Deploy (Recommended)

**For Windows (PowerShell):**
```powershell
.\deploy_to_appengine.ps1 -Quick
```

**For Linux/Mac (Bash):**
```bash
./deploy_to_appengine.sh --quick
```

### Full Deploy with Migrations

```powershell
# Windows
.\deploy_to_appengine.ps1

# Linux/Mac
./deploy_to_appengine.sh
```

After deployment, run migrations:

```bash
# 1. Connect to Cloud SQL
cloud_sql_proxy -instances=whatsapp-bulk-messaging-480620:asia-southeast1:whatsapp-db=tcp:5432

# 2. Run migrations
python manage.py migrate
```

## 📊 Admin Interface

All conversation components are manageable via Django Admin:

- **Contest Conversation Steps**: View/edit steps for each contest
- **User Conversation Progress**: Track user progress through flows
- **Contests**: Main contest management (now with conversation steps)

Access at: `https://your-app.appspot.com/admin/`

## 🐛 Troubleshooting

### Issue: Users not advancing through steps

**Solution**: Check that:
1. `auto_advance_to_next` is enabled on the step
2. Keywords are correct (case-insensitive)
3. User sent a message containing the keyword

### Issue: Multiple replies sent

**Solution**: Ensure:
1. Keywords don't overlap between contests
2. Set correct priority levels
3. Only one contest should match per message

### Issue: Old keyword system not working

**Solution**: 
- Contests WITHOUT conversation steps will use the old simple keyword system
- Contests WITH conversation steps will use the new flow system
- Both can coexist!

## 💡 Best Practices

1. **Clear Instructions**: Each step should clearly tell users what to do next
2. **Flexible Keywords**: Include variations (e.g., "PHOTO", "IMAGE", "PIC")
3. **Limit Steps**: 3-5 steps is optimal; too many gets confusing
4. **Test Thoroughly**: Test the full conversation flow before going live
5. **Monitor Progress**: Use admin panel to track user completion rates

## 📚 API Reference

### `ConversationFlowService.process_message()`
Process incoming message and advance conversation.

**Parameters:**
- `customer` (Customer): The user sending message
- `message_text` (str): Message content
- `tenant` (Tenant): Tenant context
- `conversation` (Conversation, optional): Current conversation

**Returns:** Dictionary with match results and actions taken

### `ConversationFlowService.reset_conversation()`
Reset user's progress in a specific contest.

**Parameters:**
- `customer` (Customer): The user
- `contest` (Contest): Which contest to reset

**Returns:** Boolean success status

### `ConversationFlowService.get_conversation_status()`
Get current status of user's progress.

**Parameters:**
- `customer` (Customer): The user
- `contest` (Contest): Which contest

**Returns:** Dictionary with progress details

## 🎨 Customization

The conversation flow system is highly extensible:

- Add custom validation logic in service
- Integrate with external APIs
- Add conditional branching
- Implement time-based flows
- Create dynamic step generation

## 📞 Support

For issues or questions:
1. Check the logs: `gcloud app logs tail -s default`
2. Review admin panel for progress tracking
3. Examine webhook logs for message processing

## 🎉 Happy Building!

You now have a powerful conversational contest system. Create engaging, step-by-step experiences for your users!

