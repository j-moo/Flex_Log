from django.db import migrations


CATEGORY_RENAMES = (
    ('?앸퉬', '식비'),
    ('援먰넻鍮?', '교통비'),
    ('臾명솕?앺솢', '문화생활'),
    ('?섎쪟', '의류'),
    ('怨듦낵湲?', '공과금'),
    ('移댄럹', '카페'),
    ('援щ룆', '구독'),
    ('湲고?', '기타'),
)

DEFAULT_CATEGORIES = tuple(name for _, name in CATEGORY_RENAMES)


def normalize_categories(apps, schema_editor):
    category_model = apps.get_model('expenses', 'Category')
    expense_log_model = apps.get_model('expenses', 'ExpenseLog')

    for bad_name, good_name in CATEGORY_RENAMES:
        bad_category = category_model.objects.filter(name=bad_name).first()
        good_category = category_model.objects.filter(name=good_name).first()

        if bad_category and good_category:
            expense_log_model.objects.filter(category=bad_category).update(category=good_category)
            bad_category.delete()
        elif bad_category:
            bad_category.name = good_name
            bad_category.save(update_fields=('name',))
        else:
            category_model.objects.get_or_create(name=good_name)

    for name in DEFAULT_CATEGORIES:
        category_model.objects.get_or_create(name=name)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('expenses', '0003_remove_expenselog_expenses_ex_is_visi_6bc24e_idx_and_more'),
    ]

    operations = [
        migrations.RunPython(normalize_categories, noop_reverse),
    ]
