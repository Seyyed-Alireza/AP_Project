from rest_framework import serializers
from .models import Product, Comment
from accounts.models import ProductSearchHistory

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
class ProductSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)  
    is_liked = serializers.SerializerMethodField()
    skin_types = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        exclude_fields = ['name_en', 'brand_en']
        for field in exclude_fields:
            self.fields.pop(field, None)

    def get_is_liked(self, obj):
        request = self.context.get("request")
        user_id = request.query_params.get("user_id")
        if user_id:
            return ProductSearchHistory.objects.filter(user_id=user_id, product=obj, interaction_type='like').exists()
        return False
    
    def get_skin_types(self, obj):
        return obj.get_skin_types_fa()

    def get_category(self, obj):
        return obj.get_category_display_fa()