# Generated migration for OCR integration fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0014_introduction_and_flow_updates'),
    ]

    operations = [
        migrations.AddField(
            model_name='contestentry',
            name='store_name',
            field=models.CharField(blank=True, help_text='Store name extracted by OCR', max_length=300, null=True),
        ),
        migrations.AddField(
            model_name='contestentry',
            name='store_location',
            field=models.CharField(blank=True, help_text='Store location extracted by OCR', max_length=300, null=True),
        ),
        migrations.AddField(
            model_name='contestentry',
            name='products_purchased',
            field=models.JSONField(blank=True, default=list, help_text='Products extracted by OCR: [{"name": "...", "quantity": 1}, ...]'),
        ),
        migrations.AddField(
            model_name='contestentry',
            name='rejection_reason',
            field=models.TextField(blank=True, help_text='Reason for rejection if status is rejected', null=True),
        ),
    ]

