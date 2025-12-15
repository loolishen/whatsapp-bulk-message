# Generated migration for enhancing PromptReply model with keyword auto-reply features

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0010_customergroup_blastcampaign_blastrecipient_and_more'),
    ]

    operations = [
        # Add contest foreign key to PromptReply
        migrations.AddField(
            model_name='promptreply',
            name='contest',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='prompt_replies',
                to='messaging.contest',
                help_text='Link to specific contest (optional)'
            ),
        ),
        
        # Rename body to maintain existing data
        # (No change needed - body already exists)
        
        # Add keywords field
        migrations.AddField(
            model_name='promptreply',
            name='keywords',
            field=models.TextField(
                default='',
                help_text='Comma-separated keywords (e.g., JOIN,MASUK,SERTAI)'
            ),
            preserve_default=False,
        ),
        
        # Add image_url field
        migrations.AddField(
            model_name='promptreply',
            name='image_url',
            field=models.URLField(
                blank=True,
                null=True,
                help_text='Optional image URL to send with reply'
            ),
        ),
        
        # Add is_active field
        migrations.AddField(
            model_name='promptreply',
            name='is_active',
            field=models.BooleanField(default=True, help_text='Whether this auto-reply is active'),
        ),
        
        # Add priority field
        migrations.AddField(
            model_name='promptreply',
            name='priority',
            field=models.IntegerField(
                default=0,
                help_text='Higher priority = checked first'
            ),
        ),
        
        # Add trigger_count field
        migrations.AddField(
            model_name='promptreply',
            name='trigger_count',
            field=models.IntegerField(
                default=0,
                help_text='Number of times this reply has been triggered'
            ),
        ),
        
        # Add last_triggered_at field
        migrations.AddField(
            model_name='promptreply',
            name='last_triggered_at',
            field=models.DateTimeField(
                blank=True,
                null=True,
                help_text='Last time this reply was triggered'
            ),
        ),
        
        # Add updated_at field
        migrations.AddField(
            model_name='promptreply',
            name='updated_at',
            field=models.DateTimeField(
                auto_now=True,
                help_text='Last update timestamp'
            ),
        ),
        
        # Update model metadata
        migrations.AlterModelOptions(
            name='promptreply',
            options={
                'ordering': ['-priority', '-created_at'],
                'verbose_name': 'Keyword Auto-Reply',
                'verbose_name_plural': 'Keyword Auto-Replies',
            },
        ),
    ]


