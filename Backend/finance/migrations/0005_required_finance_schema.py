import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0004_stockholding'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Commodity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=20, unique=True)),
                ('name', models.CharField(max_length=50)),
                ('unit', models.CharField(max_length=30)),
                ('currency', models.CharField(default='USD', max_length=3)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ('code',)},
        ),
        migrations.CreateModel(
            name='CommodityPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price_date', models.DateField()),
                ('close_price', models.DecimalField(decimal_places=6, max_digits=18)),
                ('open_price', models.DecimalField(blank=True, decimal_places=6, max_digits=18, null=True)),
                ('high_price', models.DecimalField(blank=True, decimal_places=6, max_digits=18, null=True)),
                ('low_price', models.DecimalField(blank=True, decimal_places=6, max_digits=18, null=True)),
                ('source', models.CharField(blank=True, max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ('price_date',)},
        ),
        migrations.CreateModel(
            name='UserFinancialProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('active', '가입 중'), ('cancelled', '해지')], default='active', max_length=10)),
                ('joined_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('cancelled_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ('-joined_at',)},
        ),
        migrations.AddField(
            model_name='financialproductrecommendation',
            name='option',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='financial_product_recommendations', to='finance.financialproductoption'),
        ),
        migrations.AlterField(
            model_name='financialproductoption',
            name='intr_rate',
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=7, null=True),
        ),
        migrations.AlterField(
            model_name='financialproductoption',
            name='intr_rate2',
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=7, null=True),
        ),
        migrations.AlterField(
            model_name='financialproductoption',
            name='save_trm',
            field=models.PositiveSmallIntegerField(),
        ),
        migrations.AlterField(
            model_name='financialproductrecommendation',
            name='interest_rate',
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=7, null=True),
        ),
        migrations.AlterField(
            model_name='financialproductrecommendation',
            name='max_interest_rate',
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=7, null=True),
        ),
        migrations.AlterField(
            model_name='financialproductrecommendation',
            name='save_trm',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddConstraint(
            model_name='financialproductoption',
            constraint=models.CheckConstraint(condition=models.Q(('save_trm__gt', 0)), name='financial_option_term_positive'),
        ),
        migrations.AddConstraint(
            model_name='financialproductoption',
            constraint=models.CheckConstraint(condition=models.Q(('intr_rate__isnull', True), ('intr_rate__gte', 0), _connector='OR'), name='financial_option_rate_nonnegative'),
        ),
        migrations.AddConstraint(
            model_name='financialproductoption',
            constraint=models.CheckConstraint(condition=models.Q(('intr_rate2__isnull', True), ('intr_rate2__gte', 0), _connector='OR'), name='financial_option_max_rate_nonnegative'),
        ),
        migrations.AddConstraint(
            model_name='commodity',
            constraint=models.CheckConstraint(condition=models.Q(('code__in', ['GOLD', 'SILVER'])), name='commodity_valid_code'),
        ),
        migrations.AddField(
            model_name='commodityprice',
            name='commodity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prices', to='finance.commodity'),
        ),
        migrations.AddField(
            model_name='userfinancialproduct',
            name='option',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='user_subscriptions', to='finance.financialproductoption'),
        ),
        migrations.AddField(
            model_name='userfinancialproduct',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='joined_financial_products', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddIndex(
            model_name='commodityprice',
            index=models.Index(fields=['commodity', 'price_date'], name='commodity_asset_date_idx'),
        ),
        migrations.AddConstraint(
            model_name='commodityprice',
            constraint=models.UniqueConstraint(fields=('commodity', 'price_date'), name='commodity_price_unique_asset_date'),
        ),
        migrations.AddConstraint(
            model_name='commodityprice',
            constraint=models.CheckConstraint(condition=models.Q(('close_price__gte', 0)), name='commodity_price_close_nonnegative'),
        ),
        migrations.AddConstraint(
            model_name='commodityprice',
            constraint=models.CheckConstraint(condition=models.Q(('open_price__isnull', True), ('open_price__gte', 0), _connector='OR'), name='commodity_price_open_nonnegative'),
        ),
        migrations.AddConstraint(
            model_name='commodityprice',
            constraint=models.CheckConstraint(condition=models.Q(('high_price__isnull', True), ('high_price__gte', 0), _connector='OR'), name='commodity_price_high_nonnegative'),
        ),
        migrations.AddConstraint(
            model_name='commodityprice',
            constraint=models.CheckConstraint(condition=models.Q(('low_price__isnull', True), ('low_price__gte', 0), _connector='OR'), name='commodity_price_low_nonnegative'),
        ),
        migrations.AddIndex(
            model_name='userfinancialproduct',
            index=models.Index(fields=['user', 'status'], name='user_fin_product_status_idx'),
        ),
        migrations.AddConstraint(
            model_name='userfinancialproduct',
            constraint=models.UniqueConstraint(fields=('user', 'option'), name='user_financial_product_unique_user_option'),
        ),
        migrations.AddConstraint(
            model_name='userfinancialproduct',
            constraint=models.CheckConstraint(condition=models.Q(('status__in', ['active', 'cancelled'])), name='user_financial_product_valid_status'),
        ),
        migrations.AddConstraint(
            model_name='userfinancialproduct',
            constraint=models.CheckConstraint(condition=models.Q(models.Q(('cancelled_at__isnull', True), ('status', 'active')), models.Q(('cancelled_at__isnull', False), ('status', 'cancelled')), _connector='OR'), name='user_financial_product_status_date_consistent'),
        ),
    ]
