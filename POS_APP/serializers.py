from rest_framework import serializers
from .models import Category, Product, Customer, Sale, SalesDetail, Employee

# Category
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

# Product
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

# Customer
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

# Employee
class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'emp_name', 'emp_number', 'email', 'address']

# Sales Detail
class SalesDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = SalesDetail
        fields = ['product', 'product_name', 'quantity', 'price']

# Main Sale Serializer
class SaleSerializer(serializers.ModelSerializer):
    products = serializers.ListField(write_only=True)
    
    # Foreign Keys
    customer_id = serializers.PrimaryKeyRelatedField(
        source='customer',
        queryset=Customer.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )
    created_by_id = serializers.PrimaryKeyRelatedField(
        source='created_by',
        queryset=Employee.objects.all(),
        write_only=True
    )

    # Read-only fields
    customer = CustomerSerializer(read_only=True)
    created_by = EmployeeSerializer(read_only=True)
    sale_details = SalesDetailSerializer(source='details', many=True, read_only=True)

    class Meta:
        model = Sale
        fields = [
            'id',
            'total_amount',
            'customer',
            'customer_id',
            'created_by',
            'created_by_id',
            'sale_date',
            'products',
            'sale_details',
            'payment_method',
        ]

    def create(self, validated_data):
        products_data = validated_data.pop('products', [])
        sale = Sale.objects.create(**validated_data)

        for item in products_data:
            product_name = item.get('name')
            quantity = item.get('quantity')
            price = item.get('price')

            product = Product.objects.filter(name=product_name).first()
            if not product:
                raise serializers.ValidationError(f"Product '{product_name}' not found.")

            SalesDetail.objects.create(
                sale=sale,
                product=product,
                quantity=quantity,
                price=price,
            )

        return sale

# Optional: Extended detail view
class SalesDetailNestedSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = SalesDetail
        fields = ['product', 'product_name', 'quantity', 'price', 'total_price']

    def get_total_price(self, obj):
        return float(obj.quantity) * float(obj.price)


class EmployeeLoginSerializer(serializers.Serializer):
    emp_email = serializers.EmailField()
    password = serializers.CharField()

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'emp_name', 'emp_number', 'emp_email', 'emp_address']