# serializers.py
from rest_framework import serializers
from .models import SGSKPIsDelDev  # Ensure SGSKPIsDelDev exists in models.py

class SGSKPIsDelDevSerializer(serializers.ModelSerializer):
    class Meta:
        model = SGSKPIsDelDev
        fields = '__all__'  # Change to a list of fields if needed, e.g., ['field1', 'field2']

# your_app/serializers.py

from rest_framework import serializers
from .models import CompanyLogin
from .models import UserProfile


class CompanyLoginSerializer(serializers.ModelSerializer):
    company_code = serializers.CharField(write_only=True)

    class Meta:
        model = CompanyLogin
        fields = ['company', 'company_code', 'region', 'country', 'profile_photo']

    def validate_company_code(self, value):
        try:
            return UserProfile.objects.get(company_code=value)
        except UserProfile.DoesNotExist:
            raise serializers.ValidationError("Invalid company code")

    def create(self, validated_data):
        user_profile = validated_data.pop('company_code')
        return CompanyLogin.objects.create(company_code=user_profile, **validated_data)
    

from .models import PerfMgmtAssessment

class PerfMgmtAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerfMgmtAssessment
        fields = '__all__'