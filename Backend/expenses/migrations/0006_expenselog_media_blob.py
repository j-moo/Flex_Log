from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expenses', '0005_expenselog_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='expenselog',
            name='media_data',
            field=models.BinaryField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='expenselog',
            name='media_content_type',
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name='expenselog',
            name='media_name',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
