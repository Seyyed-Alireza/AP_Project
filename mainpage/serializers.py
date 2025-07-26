from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        exclude_fields = ['name_en', 'brand_en']
        for field in exclude_fields:
            self.fields.pop(field, None)