from rest_framework import generics
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated

from .models import Category, ExpenseLog
from .serializers import CategorySerializer, ExpenseLogSerializer


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticated,)


class ExpenseLogListCreateView(generics.ListCreateAPIView):
    serializer_class = ExpenseLogSerializer
    permission_classes = (IsAuthenticated,)
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def get_queryset(self):
        return ExpenseLog.objects.filter(user=self.request.user).select_related(
            'user',
            'category',
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ExpenseLogDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ExpenseLogSerializer
    permission_classes = (IsAuthenticated,)
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def get_queryset(self):
        return ExpenseLog.objects.filter(user=self.request.user).select_related(
            'user',
            'category',
        )
