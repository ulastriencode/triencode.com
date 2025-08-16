from django.db import migrations, models
from django.db.models.functions import Lower

class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='domain',
            index=models.Index(
                Lower('domain'),
                name='domain_lower_idx',
            ),
        ),
    ]
