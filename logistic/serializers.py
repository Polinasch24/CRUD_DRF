from rest_framework import serializers
from logistic.models import Product, Stock, StockProduct
from rest_framework.exceptions import ValidationError


class ProductSerializer(serializers.ModelSerializer):
    # настройте сериализатор для продукта
    class Meta:
        model = Product
        fields = ['id','title', 'description']

        def validate_text(self, value):
            if 'product' in value:
                raise ValidationError('Вы использовали запрещенное слово')
            return value


class ProductPositionSerializer(serializers.ModelSerializer):
    # настройте сериализатор для позиции продукта на складе
    class Meta:
        model = StockProduct
        fields = ['id','product', 'quantity', 'price']


class StockSerializer(serializers.ModelSerializer):
    positions = ProductPositionSerializer(many=True)

    # настройте сериализатор для склада
    class Meta:
        model = Stock
        fields = ['address', 'positions']

    def create(self, validated_data):
        # достаем связанные данные для других таблиц
        positions = validated_data.pop('positions')

        # создаем склад по его параметрам
        stock = super().create(validated_data)
        # здесь вам надо заполнить связанные таблицы
        # в нашем случае: таблицу StockProduct
        # с помощью списка positions

        for position in positions:
            store = StockProduct.objects.create(stock=stock, **position)
            store.save()
        return stock

    def update(self, instance, validated_data):
        # достаем связанные данные для других таблиц
        positions = validated_data.pop('positions')

        # обновляем склад по его параметрам
        stock = super().update(instance, validated_data)

        # здесь вам надо обновить связанные таблицы
        # в нашем случае: таблицу StockProduct
        # с помощью списка positions

        for position in positions:
            store = StockProduct.objects.update_or_create(
                stock=stock,
                product=position['product'],
                defaults={
                    'stock': stock,
                    'product': position['product'],
                    'quantity': position['quantity'],
                    'price': position['price']
                    }
            )
            store.save()

        return stock