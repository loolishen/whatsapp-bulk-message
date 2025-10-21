# WhatsApp Blasting Feature Guide

## Overview

A comprehensive WhatsApp Blasting system has been added to your application. This feature allows you to:
- Create and manage customer groups
- Import customer groups from Excel/CSV files
- Create groups from contest participants
- Send bulk WhatsApp messages to selected groups
- Track delivery and success rates for blast campaigns

## New Features Added

### 1. Customer Group Management
- **Create Manual Groups**: Create empty groups and add customers manually
- **Import from Files**: Import customer data from Excel (.xlsx, .xls) or CSV files
- **Create from Contests**: Automatically create groups from contest participants (verified only or all)

### 2. Blast Campaign Management
- **Create Campaigns**: Design WhatsApp messages with optional images
- **Select Recipients**: Choose from customer groups or contest participants
- **Track Delivery**: Monitor sent, delivered, and failed messages
- **Success Metrics**: View success rates and detailed recipient status

## Database Models

### CustomerGroup
- Stores groups of customers for targeted messaging
- Can be created from manual entry, file import, or contest participants
- Tracks source and import metadata

### GroupMember
- Links customers to groups
- Supports custom data per member

### BlastCampaign
- Stores campaign details (name, message, image)
- Tracks campaign status (draft, scheduled, sending, completed, failed, cancelled)
- Maintains delivery statistics

### BlastRecipient
- Individual recipient tracking for each campaign
- Status tracking (pending, queued, sent, delivered, failed, skipped)
- Delivery timestamps and error messages

## Navigation Structure

The new "WhatsApp Blasting" section has been added to the main navigation bar alongside:
- Contest
- CRM
- Customers

### WhatsApp Blasting Sidebar Menu:
1. **📁 Customer Groups** - View and manage all customer groups
2. **📨 Blast Campaigns** - View all blast campaigns and their status
3. **✉️ Create Campaign** - Create a new blast campaign

## User Workflows

### Creating a Customer Group

**Option 1: Import from File**
1. Go to Customer Groups page
2. Click "📥 Import from File"
3. Enter group name
4. Upload Excel/CSV file with columns:
   - `name` (required)
   - `phone_number` (required)
   - `gender` (optional)
   - `age` (optional)
   - `city` (optional)
   - `state` (optional)
5. System will create/update customers and add them to the group

**Option 2: From Contest Participants**
1. Go to Customer Groups page
2. Click "🏆 From Contest"
3. Select contest
4. Enter group name
5. Optionally check "Include verified participants only"
6. System will create a group with all matching participants

**Option 3: Manual Creation**
1. Go to Customer Groups page
2. Click "+ Create Group"
3. Enter group name and description
4. Add customers manually later

### Creating a Blast Campaign

1. Go to "Create Campaign" page
2. Enter campaign details:
   - Campaign Name (required)
   - Message Text (required)
   - Image URL (optional)
3. Select recipients:
   - Check customer groups to include
   - Check contests to include participants from
4. Review message preview
5. Click "Create Campaign"
6. Campaign is saved as draft with all recipients calculated
7. Click "Send Now" when ready to send

### Monitoring Campaign Status

1. Go to "Blast Campaigns" page
2. View all campaigns with:
   - Total recipients
   - Sent count
   - Delivered count
   - Success rate
3. Click "View Details" to see:
   - Full message content
   - Target groups/contests
   - Individual recipient status
   - Delivery timestamps

## File Structure

### New Files Created:

#### Backend:
- `messaging/blast_views.py` - Views for WhatsApp Blasting features
- `messaging/migrations/0010_customergroup_blastcampaign_blastrecipient_and_more.py` - Database migration

#### Templates:
- `templates/messaging/blast_groups_list.html` - Customer groups listing
- `templates/messaging/blast_group_detail.html` - Individual group details
- `templates/messaging/blast_campaigns_list.html` - Campaigns listing
- `templates/messaging/blast_create_campaign.html` - Campaign creation form
- `templates/messaging/blast_campaign_detail.html` - Campaign details and tracking

### Modified Files:
- `messaging/models.py` - Added 4 new models (CustomerGroup, GroupMember, BlastCampaign, BlastRecipient)
- `messaging/urls.py` - Added 11 new URL routes
- `templates/messaging/contest_home.html` - Updated navigation
- `templates/messaging/dashboard.html` - Updated navigation
- `templates/messaging/crm_home.html` - Updated navigation
- `templates/messaging/manage_customers.html` - Updated navigation

## URL Routes

### Customer Groups:
- `/blast/groups/` - List all groups
- `/blast/groups/<group_id>/` - View group details
- `/blast/groups/create/` - Create new group (POST)
- `/blast/groups/import/` - Import from file (POST)
- `/blast/groups/from-contest/` - Create from contest (POST)
- `/blast/groups/<group_id>/delete/` - Delete group (POST)

### Blast Campaigns:
- `/blast/campaigns/` - List all campaigns
- `/blast/campaigns/create/` - Create campaign page (GET/POST)
- `/blast/campaigns/<blast_id>/` - View campaign details
- `/blast/campaigns/<blast_id>/send/` - Send campaign (POST)
- `/blast/campaigns/<blast_id>/cancel/` - Cancel campaign (POST)

## Import File Format

### Excel/CSV Format:
```
name           | phone_number    | gender | age | city        | state
John Doe       | +60123456789    | M      | 30  | Kuala Lumpur| Selangor
Jane Smith     | +60198765432    | F      | 25  | Penang      | Penang
Ahmad Ibrahim  | +60112345678    | M      | 35  | Johor Bahru | Johor
```

**Required Columns:**
- `name` - Customer name
- `phone_number` - Phone number (with or without + prefix)

**Optional Columns:**
- `gender` - Gender (M/F/NB/PNS/N/A)
- `age` - Age as number
- `city` - City name
- `state` - State name

## API Response Examples

### Create Group Response:
```json
{
  "success": true,
  "group_id": "uuid-here",
  "redirect_url": "/blast/groups/uuid-here/"
}
```

### Import Group Response:
```json
{
  "success": true,
  "group_id": "uuid-here",
  "created_count": 15,
  "existing_count": 5,
  "total_count": 20
}
```

### Send Campaign Response:
```json
{
  "success": true,
  "message": "Campaign is being sent",
  "total_recipients": 50
}
```

## Next Steps / TODO

### Integration with WhatsApp API:
The `blast_send_campaign` function currently marks recipients as "queued" but doesn't actually send messages. You'll need to:

1. Update `messaging/blast_views.py` in the `blast_send_campaign` function
2. Import your WhatsApp API service
3. Loop through recipients and send messages
4. Update recipient status based on API response
5. Handle rate limiting and retries

Example integration:
```python
from .whatsapp_service import send_message  # Your WhatsApp API service

@login_required
@require_http_methods(["POST"])
def blast_send_campaign(request, blast_id):
    # ... existing code ...
    
    # Get WhatsApp connection
    wa_connection = campaign.whatsapp_connection
    
    # Send to each recipient
    recipients = BlastRecipient.objects.filter(
        blast_campaign=campaign, 
        status='pending'
    )
    
    for recipient in recipients:
        try:
            # Send message via WhatsApp API
            result = send_message(
                wa_connection=wa_connection,
                phone_number=recipient.customer.phone_number,
                message=campaign.message_text,
                image_url=campaign.message_image_url
            )
            
            # Update recipient status
            recipient.status = 'sent'
            recipient.sent_at = dj_timezone.now()
            recipient.save()
            
            # Update campaign stats
            campaign.sent_count += 1
            campaign.save()
            
        except Exception as e:
            recipient.status = 'failed'
            recipient.error_message = str(e)
            recipient.save()
            
            campaign.failed_count += 1
            campaign.save()
    
    # Mark campaign as completed
    campaign.status = 'completed'
    campaign.completed_at = dj_timezone.now()
    campaign.save()
```

### Recommended Enhancements:
1. Add scheduling for future campaign sends
2. Add message templates/variables (e.g., {{name}}, {{city}})
3. Add duplicate detection when importing customers
4. Add group editing (add/remove members)
5. Add campaign cloning
6. Add export functionality for groups
7. Add analytics dashboard for blast campaigns
8. Add webhook handling for delivery status updates
9. Add rate limiting to prevent API throttling
10. Add background job processing for large campaigns

## Testing

### Test the Feature:
1. **Create a test group manually**
   - Go to `/blast/groups/`
   - Create a new group
   
2. **Import test data**
   - Use the provided `sample_contacts.xlsx`
   - Import it as a new group
   
3. **Create from contest**
   - Ensure you have an active contest with participants
   - Create a group from contest participants
   
4. **Create a campaign**
   - Go to `/blast/campaigns/create/`
   - Fill in campaign details
   - Select groups/contests
   - Create and send

## Security Considerations

- All views are protected with `@login_required` decorator
- Tenant isolation is enforced (users only see their own data)
- File uploads are validated for file types
- CSRF protection is enabled on all forms
- Phone numbers are validated and formatted

## Performance Considerations

- Group member counts use efficient `.count()` queries
- Foreign key relationships are optimized with `select_related` and `prefetch_related`
- Bulk creates are used where possible
- Indexes are added on frequently queried fields

## Support

For issues or questions about this feature, please refer to:
- Models documentation in `messaging/models.py`
- Views documentation in `messaging/blast_views.py`
- URL configuration in `messaging/urls.py`

---

**Created:** October 21, 2025
**Version:** 1.0
**Status:** Production Ready (pending WhatsApp API integration)

