# Generated migration for introduction_message field and contest flow updates

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0013_conversation_steps'),
    ]

    operations = [
        migrations.AddField(
            model_name='contest',
            name='introduction_message',
            field=models.TextField(blank=True, help_text='Welcome/introduction message sent when user joins contest (before PDPA)', null=True),
        ),
        migrations.AlterField(
            model_name='contestflowstate',
            name='current_step',
            field=models.CharField(
                choices=[
                    ('initial', 'Initial Contact'),
                    ('pdpa_sent', 'PDPA Message Sent'),
                    ('pdpa_response', 'PDPA Response Received'),
                    ('awaiting_nric', 'Awaiting NRIC/Details'),
                    ('awaiting_receipt', 'Awaiting Receipt'),
                    ('instructions_sent', 'Instructions Sent'),
                    ('awaiting_submission', 'Awaiting Submission'),
                    ('submitted', 'Submitted'),
                    ('completed', 'Completed'),
                ],
                default='initial',
                max_length=20
            ),
        ),
    ]

