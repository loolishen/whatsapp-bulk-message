#!/usr/bin/env python
"""
Script to update all templates to use the unified sidebar system
"""

import os
import re

def update_template_sidebar(template_path):
    """Update a template to use the unified sidebar system"""
    print(f"Updating {template_path}...")
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if it's a blast-related template
        is_blast_template = any(keyword in template_path.lower() for keyword in ['blast', 'campaign'])
        is_crm_template = any(keyword in template_path.lower() for keyword in ['crm', 'customer'])
        
        # Determine which sidebar to use
        if is_blast_template:
            sidebar_include = "{% include 'messaging/includes/sidebar_blast.html' %}"
        elif is_crm_template:
            sidebar_include = "{% include 'messaging/includes/sidebar_crm.html' %}"
        else:
            sidebar_include = "{% include 'messaging/includes/sidebar.html' %}"
        
        # Remove existing sidebar HTML
        sidebar_patterns = [
            r'<div class="sidebar"[^>]*>.*?</div>\s*</div>',
            r'<nav class="sidebar"[^>]*>.*?</nav>',
            r'<!-- Sidebar Navigation -->.*?</div>',
            r'<!-- Include shared sidebar styles -->',
        ]
        
        for pattern in sidebar_patterns:
            content = re.sub(pattern, '', content, flags=re.DOTALL)
        
        # Add sidebar styles include
        if '{% include \'messaging/includes/sidebar_styles.html\' %}' not in content:
            # Find the </head> tag and add before it
            head_end = content.find('</head>')
            if head_end != -1:
                content = content[:head_end] + '    {% include \'messaging/includes/sidebar_styles.html\' %}\n' + content[head_end:]
        
        # Add main content styles include
        if '{% include \'messaging/includes/main_content_styles.html\' %}' not in content:
            # Find the </head> tag and add before it
            head_end = content.find('</head>')
            if head_end != -1:
                content = content[:head_end] + '    {% include \'messaging/includes/main_content_styles.html\' %}\n' + content[head_end:]
        
        # Add sidebar include after <body>
        body_start = content.find('<body>')
        if body_start != -1:
            body_end = content.find('>', body_start) + 1
            content = content[:body_end] + '\n  ' + sidebar_include + '\n' + content[body_end:]
        
        # Update main content margin
        content = re.sub(
            r'\.main-content\s*{[^}]*margin-left:\s*\d+px[^}]*}',
            '.main-content { margin-left: 280px; padding: 24px 32px; min-height: 100vh; background: var(--gray); transition: margin-left 0.3s ease; }',
            content
        )
        
        # Write updated content
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Updated {template_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating {template_path}: {e}")
        return False

def main():
    """Update all messaging templates"""
    templates_dir = 'templates/messaging'
    
    # Templates to update (excluding the includes directory)
    templates_to_update = [
        'dashboard.html',
        'contest_home.html',
        'contest_manager.html',
        'contest_detail.html',
        'contest_create.html',
        'participants_manager.html',
        'select_winners.html',
        'blast_groups_list.html',
        'blast_campaigns_list.html',
        'blast_create_campaign.html',
        'blast_campaign_detail.html',
        'blast_group_detail.html',
        'crm_home.html',
        'crm_analytics.html',
        'crm_campaigns.html',
        'crm_schedule.html',
        'crm_prompt_replies.html',
        'manage_customers.html',
        'customer_detail.html',
        'whatsapp_settings.html',
        'incoming_messages.html',
    ]
    
    updated_count = 0
    total_count = len(templates_to_update)
    
    for template in templates_to_update:
        template_path = os.path.join(templates_dir, template)
        if os.path.exists(template_path):
            if update_template_sidebar(template_path):
                updated_count += 1
        else:
            print(f"⚠️ Template not found: {template_path}")
    
    print(f"\n🎉 Updated {updated_count}/{total_count} templates successfully!")
    print("\n📋 Summary:")
    print("✅ All templates now use unified sidebar system")
    print("✅ Consistent navigation across all pages")
    print("✅ Mobile-responsive sidebar")
    print("✅ Improved UI/UX with better visual hierarchy")

if __name__ == "__main__":
    main()

