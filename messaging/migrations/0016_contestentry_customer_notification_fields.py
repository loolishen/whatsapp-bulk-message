from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("messaging", "0015_ocr_integration_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="contestentry",
            name="last_customer_notification_status",
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name="contestentry",
            name="last_customer_notification_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]




