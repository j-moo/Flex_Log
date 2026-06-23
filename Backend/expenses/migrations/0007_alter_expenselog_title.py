from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expenses', '0006_expenselog_media_blob'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expenselog',
            name='title',
            field=models.CharField(blank=True, default='', max_length=150),
        ),
    ]
