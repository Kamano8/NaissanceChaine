import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('actes', '0004_alter_actenaissance_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='actenaissance',
            name='uuid_enfant',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='Identifiant unique enfant (UUID)'),
        ),
    ]
