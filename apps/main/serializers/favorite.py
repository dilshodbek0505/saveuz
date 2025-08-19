from rest_framework import serializers

from apps.main.models import Favorite

class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ("id", "user", "product", "market")
        read_only_fields = ("id", "user")
    
    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)

    def to_representation(self, instance):
        from apps.product.serializers import ProductSerializer, MarketSerializer
        self.fields["market"] = MarketSerializer()
        self.fields["product"] = ProductSerializer()
        
        return super().to_representation(instance)    
    