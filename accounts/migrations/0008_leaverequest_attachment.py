from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_alter_worker_worker_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='leaverequest',
            name='attachment',
            field=models.FileField(blank=True, null=True, upload_to='leave_attachments/'),
        ),
    ]
