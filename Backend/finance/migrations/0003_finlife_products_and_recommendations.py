# Generated for FinLife financial product fixtures and recommendations.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0003_monthlyaianalysis'),
        ('finance', '0002_remove_productrecommendation_product_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FinancialProduct',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'product_type',
                    models.CharField(
                        choices=[('deposit', '정기예금'), ('saving', '정기적금')],
                        max_length=20,
                    ),
                ),
                ('fin_prdt_cd', models.CharField(max_length=100)),
                ('dcls_month', models.CharField(blank=True, max_length=20)),
                ('kor_co_nm', models.CharField(max_length=100)),
                ('fin_prdt_nm', models.CharField(max_length=200)),
                ('join_way', models.TextField(blank=True)),
                ('mtrt_int', models.TextField(blank=True)),
                ('spcl_cnd', models.TextField(blank=True)),
                ('join_deny', models.CharField(blank=True, max_length=20)),
                ('join_member', models.TextField(blank=True)),
                ('etc_note', models.TextField(blank=True)),
                ('max_limit', models.BigIntegerField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('fetched_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ('product_type', 'kor_co_nm', 'fin_prdt_nm'),
                'indexes': [
                    models.Index(
                        fields=['product_type', 'kor_co_nm'],
                        name='finance_product_type_bank_idx',
                    ),
                    models.Index(fields=['fin_prdt_cd'], name='finance_product_code_idx'),
                ],
                'constraints': [
                    models.UniqueConstraint(
                        fields=('product_type', 'fin_prdt_cd'),
                        name='financial_product_unique_type_code',
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name='FinancialProductRecommendation',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('reason', models.TextField()),
                ('action_text', models.CharField(blank=True, max_length=100)),
                ('bank_name', models.CharField(blank=True, max_length=100)),
                ('product_name', models.CharField(blank=True, max_length=200)),
                ('product_type', models.CharField(blank=True, max_length=20)),
                ('save_trm', models.CharField(blank=True, max_length=20)),
                ('interest_rate', models.FloatField(blank=True, null=True)),
                ('max_interest_rate', models.FloatField(blank=True, null=True)),
                ('ai_comment', models.TextField(blank=True)),
                ('caution', models.TextField(blank=True)),
                ('priority', models.IntegerField(default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                (
                    'analysis',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='financial_product_recommendations',
                        to='analysis.monthlyaianalysis',
                    ),
                ),
                (
                    'product',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='financial_product_recommendations',
                        to='finance.financialproduct',
                    ),
                ),
                (
                    'user',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='financial_product_recommendations',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                'ordering': ('priority', '-created_at'),
                'indexes': [
                    models.Index(
                        fields=['user', '-created_at'],
                        name='finance_reco_user_created_idx',
                    ),
                    models.Index(
                        fields=['priority', '-created_at'],
                        name='finance_reco_priority_idx',
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name='FinancialProductOption',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('intr_rate_type', models.CharField(blank=True, max_length=20)),
                ('intr_rate_type_nm', models.CharField(blank=True, max_length=50)),
                ('save_trm', models.CharField(blank=True, max_length=20)),
                ('intr_rate', models.FloatField(blank=True, null=True)),
                ('intr_rate2', models.FloatField(blank=True, null=True)),
                ('rsrv_type', models.CharField(blank=True, max_length=20)),
                ('rsrv_type_nm', models.CharField(blank=True, max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                (
                    'product',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='options',
                        to='finance.financialproduct',
                    ),
                ),
            ],
            options={
                'ordering': ('product', 'save_trm', 'intr_rate_type', 'rsrv_type'),
                'indexes': [
                    models.Index(fields=['save_trm'], name='finance_option_term_idx'),
                    models.Index(fields=['intr_rate2'], name='finance_option_rate2_idx'),
                ],
                'constraints': [
                    models.UniqueConstraint(
                        fields=('product', 'save_trm', 'intr_rate_type', 'rsrv_type'),
                        name='financial_option_unique_product_terms',
                    ),
                ],
            },
        ),
    ]
