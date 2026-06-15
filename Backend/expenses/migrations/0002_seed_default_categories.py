from django.db import migrations


DEFAULT_CATEGORIES = ('식비', '교통비', '문화생활', '쇼핑', '공과금', '카페', '구독', '기타')


def seed_categories(apps, schema_editor):
    category_model = apps.get_model('expenses', 'Category')
    for name in DEFAULT_CATEGORIES:
        category_model.objects.get_or_create(name=name)


def remove_categories(apps, schema_editor):
    category_model = apps.get_model('expenses', 'Category')
    category_model.objects.filter(name__in=DEFAULT_CATEGORIES).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('expenses', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_categories, remove_categories),
    ]
