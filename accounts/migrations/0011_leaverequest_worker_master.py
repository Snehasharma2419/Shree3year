from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_generatedreport'),
    ]

    operations = [
        migrations.AddField(
            model_name='leaverequest',
            name='worker_master',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.universityid'),
        ),
    ]
