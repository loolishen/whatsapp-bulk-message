# Generated migration for adding keyword auto-reply to Contest model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0011_enhance_promptreply_keywords'),
    ]

    operations = [
        # Add keyword auto-reply fields to Contest
        migrations.AddField(
            model_name='contest',
            name='keywords',
            field=models.TextField(
                blank=True,
                null=True,
                help_text='Comma-separated keywords that trigger this contest (e.g., JOIN,MASUK,SERTAI)'
            ),
        ),
        migrations.AddField(
            model_name='contest',
            name='auto_reply_message',
            field=models.TextField(
                blank=True,
                null=True,
                help_text='Automatic reply sent when someone sends the keyword'
            ),
        ),
        migrations.AddField(
            model_name='contest',
            name='auto_reply_priority',
            field=models.IntegerField(
                default=5,
                help_text='Priority when multiple contests match (higher = checked first)'
            ),
        ),
        
        # Remove PromptReply model (deprecated - now integrated into Contest)
        migrations.DeleteModel(
            name='PromptReply',
        ),
    ]

