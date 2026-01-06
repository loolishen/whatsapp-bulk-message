# Generated migration for ContestConversationStep and UserConversationProgress models

from django.db import migrations, models
import django.db.models.deletion
import uuid
import django.utils.timezone as dj_timezone


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0012_contest_keywords_autoreply'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContestConversationStep',
            fields=[
                ('step_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('step_order', models.IntegerField(default=1, help_text='Order of this step in the conversation (1, 2, 3...)')),
                ('step_name', models.CharField(help_text='Name of this step (e.g., "Welcome", "NRIC Request")', max_length=200)),
                ('keywords', models.TextField(help_text='Comma-separated keywords that trigger this step (e.g., JOIN,START)')),
                ('auto_reply_message', models.TextField(help_text='Message sent when keywords match')),
                ('auto_advance_to_next', models.BooleanField(default=True, help_text='Automatically advance to next step after this reply')),
                ('wait_for_response', models.BooleanField(default=True, help_text='Wait for user response before showing next step')),
                ('created_at', models.DateTimeField(default=dj_timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('contest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conversation_steps', to='messaging.contest')),
            ],
            options={
                'ordering': ['contest', 'step_order'],
                'unique_together': {('contest', 'step_order')},
            },
        ),
        migrations.CreateModel(
            name='UserConversationProgress',
            fields=[
                ('progress_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('started_at', models.DateTimeField(default=dj_timezone.now)),
                ('last_interaction_at', models.DateTimeField(auto_now=True)),
                ('completed', models.BooleanField(default=False)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('contest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_progress', to='messaging.contest')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conversation_progress', to='messaging.customer')),
                ('current_step', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='current_users', to='messaging.contestconversationstep')),
            ],
            options={
                'ordering': ['-last_interaction_at'],
                'unique_together': {('customer', 'contest')},
            },
        ),
    ]

