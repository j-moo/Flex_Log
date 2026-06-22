from django.db import migrations, models


def populate_expense_titles(apps, schema_editor):
    ExpenseLog = apps.get_model('expenses', 'ExpenseLog')
    for expense in ExpenseLog.objects.all().iterator():
        title = (
            expense.overlay_text
            or expense.product_name
            or expense.merchant
            or f'소비 기록 #{expense.pk}'
        )
        expense.title = title[:150]
        expense.save(update_fields=('title',))


class Migration(migrations.Migration):

    dependencies = [
        ('expenses', '0004_normalize_default_categories'),
    ]

    operations = [
        migrations.AddField(
            model_name='expenselog',
            name='title',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.RunPython(populate_expense_titles, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='expenselog',
            name='title',
            field=models.CharField(max_length=150),
        ),
    ]
