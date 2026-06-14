from rest_framework import serializers
from .models import FinancialProduct, ProductRecommendation
class FinancialProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialProduct
        fields = '__all__'
class ProductRecommendationSerializer(serializers.ModelSerializer):
    product = FinancialProductSerializer(read_only=True)
    class Meta:
        model = ProductRecommendation
        fields = ('id','user','ai_analysis','product','reason','priority','created_at')
        read_only_fields = ('id','user','product','reason','priority','created_at')
