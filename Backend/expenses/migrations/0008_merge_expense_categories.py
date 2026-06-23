from django.db import migrations


CATEGORY_MERGES = (
    ('카페', '식비'),
    ('의류', '쇼핑'),
)

FINAL_CATEGORIES = (
    '식비',
    '교통비',
    '문화생활',
    '쇼핑',
    '공과금',
    '구독',
    '기타',
)


def merge_categories(apps, schema_editor):
    category_model = apps.get_model('expenses', 'Category')
    expense_log_model = apps.get_model('expenses', 'ExpenseLog')

    for source_name, target_name in CATEGORY_MERGES:
        target_category, _ = category_model.objects.get_or_create(name=target_name)
        source_category = category_model.objects.filter(name=source_name).first()
        if not source_category:
            continue
        expense_log_model.objects.filter(category=source_category).update(category=target_category)
        source_category.delete()

    for name in FINAL_CATEGORIES:
        category_model.objects.get_or_create(name=name)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('expenses', '0007_alter_expenselog_title'),
    ]

    operations = [
        migrations.RunPython(merge_categories, noop_reverse),
    ]
