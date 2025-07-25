from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import (
    Category, Product, Customer, Employee,
    Sale, SalesDetail
)
from .serializers import (
    CategorySerializer, ProductSerializer,
    CustomerSerializer, SaleSerializer,
    SalesDetailSerializer, EmployeeSerializer,
    EmployeeLoginSerializer
)


class BaseAPIView(APIView):
    model = None
    serializer_class = None

    def get(self, request):
        items = self.model.objects.all()
        serializer = self.serializer_class(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        if not pk:
            return Response({"detail": "ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        instance = get_object_or_404(self.model, pk=pk)
        serializer = self.serializer_class(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        if not pk:
            return Response({"detail": "ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        instance = get_object_or_404(self.model, pk=pk)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Category API View
class CategoryAPIView(BaseAPIView):
    model = Category
    serializer_class = CategorySerializer


# Product API View
class ProductAPIView(BaseAPIView):
    model = Product
    serializer_class = ProductSerializer

    def get(self, request):
        category_id = request.query_params.get('category', None)
        products = Product.objects.filter(category_id=category_id) if category_id else Product.objects.all()
        serializer = self.serializer_class(products, many=True)
        return Response(serializer.data)


# Customer API View
class CustomerAPIView(BaseAPIView):
    model = Customer
    serializer_class = CustomerSerializer


# Employee API View
class EmployeeAPIView(BaseAPIView):
    model = Employee
    serializer_class = EmployeeSerializer


# Sale and SaleDetails API View
class SaleAPIView(BaseAPIView):
    model = Sale
    serializer_class = SaleSerializer


class SalesDetailAPIView(BaseAPIView):
    model = SalesDetail
    serializer_class = SalesDetailSerializer


# Sale Create API View
class SaleCreateAPIView(APIView):
    GUEST_CUSTOMER_ID = 1  # Fallback customer

    def get(self, request):
        sales = Sale.objects.all().order_by('-sale_date')
        serializer = SaleSerializer(sales, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data
        print("📦 Incoming request data:", data)
        
        products_data = data.get("products")
        total_amount = float(data.get("total_amount"))
        total_quantity = int(data.get("total_quantity"))        
        emp_id = data.get("employee_id")
        customer_data = data.get("customer")
        # total_quantity = data.get("total_quantity")
        payment_method = data.get("payment_method", "Cash")
        print("Products:", products_data)
        print("Total Amount:", total_amount)
        print("Employee ID:", emp_id)
        print("Customer Data:", customer_data)
        emp_id = data.get("emp_id")
        print(f"Employee ID from request data: {emp_id}")
        # Check required fields
        if not products_data or total_amount is None or not emp_id:
            return Response({"error": "Missing products, amount, or emp_id."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                # Handle Customer creation or update
                if customer_data and customer_data.get("phone"):
                    phone = customer_data["phone"].strip()
                    name = customer_data.get("name", "").strip()

                    customer, created = Customer.objects.get_or_create(
                        phone=phone,
                        defaults={"first_name": name}
                    )
                    if not created and name and customer.first_name != name:
                        customer.first_name = name
                        customer.save()
                else:
                    customer = Customer.objects.get(id=self.GUEST_CUSTOMER_ID)

                # Get Employee
                employee = get_object_or_404(Employee, pk=emp_id)

                # Create Sale
                sale = Sale.objects.create(
                    customer=customer,
                    total_amount=total_amount,
                    created_by=employee,
                    payment_method=payment_method
                )

                # Create Sale Details
                for item in products_data:
                    product_name = item["name"]
                    quantity = item["quantity"]
                    price = item["price"]
                    print(f"📦 Processing product: {product_name}, Quantity: {quantity}, Price: {price}")

                    product = Product.objects.filter(name=product_name).first()
                    if not product:
                        return Response({"error": f"Product '{product_name}' not found."}, status=status.HTTP_400_BAD_REQUEST)

                    # Create SalesDetail record
                    SalesDetail.objects.create(
                        sale=sale,
                        product=product,
                        quantity=quantity,
                        price=price
                    )

                return Response({
                    "message": "Sale created successfully.",
                    "sale_id": sale.id,
                    "total_amount": str(sale.total_amount),
                    "total_quantity": total_quantity
                }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Employee Login API View


class EmployeeLoginAPIView(APIView):
    def post(self, request):
        serializer = EmployeeLoginSerializer(data=request.data)
        if serializer.is_valid():
            emp_email = serializer.validated_data['emp_email']
            password = serializer.validated_data['password']

            try:
                employee = Employee.objects.get(emp_email=emp_email, password=password)
                return Response({
                    "message": "Login successful",
                    "employee_id": employee.id,
                    "employee": EmployeeSerializer(employee).data
                }, status=status.HTTP_200_OK)

            except Employee.DoesNotExist:
                return Response({"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)