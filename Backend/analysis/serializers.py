from rest_framework import serializers
from .models import AIAnalysis, MonthlyAnalysis
class MonthlyAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlyAnalysis
        fields = '__all__'
        read_only_fields = ('user','total_amount','category_summary')
class AIAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIAnalysis
        fields = '__all__'
        read_only_fields = ('user','input_summary','result','feedback','status')
