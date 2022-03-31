from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from .serializers import UserSerializer, DatasetSerializer, MLModelSerializer, LoadDatasetSerializer, CreateModelSerializer, ResultSerializer
from .models import Dataset, MLModel, UploadedFile

# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer

class DatasetViewSet(viewsets.ModelViewSet):
    serializer_class = DatasetSerializer

    def get_queryset(self):
        if self.request.user.is_anonymous:
            return
        if self.request.user.is_superuser:
            return Dataset.objects.all()
        return Dataset.objects.filter(creator = self.request.user)

class MLModelViewSet(viewsets.ModelViewSet):
    serializer_class = MLModelSerializer

    def get_queryset(self):
        if self.request.user.is_anonymous:
            return
        if self.request.user.is_superuser:
            return MLModel.objects.all()
        return MLModel.objects.filter(creator = self.request.user)

class UploadFileView(viewsets.ModelViewSet):
    serializer_class = LoadDatasetSerializer

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES['file']
        request.data['name'] = file_obj.name
        file_serializer = LoadDatasetSerializer(data=request.data, context={'request': request})

        try:
            if file_serializer.is_valid():
                file_serializer.save()
                return Response(file_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except(IntegrityError):
            return Response({'IntegrityError': f'File with name {file_obj.name} already exists.' }, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        if self.request.user.is_anonymous:
            return
        #if self.request.user.is_superuser:
            #return UploadedFile.objects.all()
        return UploadedFile.objects.filter(creator = self.request.user)

class CreateModelView(generics.CreateAPIView):
    serializer_class = CreateModelSerializer

    def post(self, request, *args, **kwargs):
        file_serializer = CreateModelSerializer(data=request.data, context={'request': request})

        if file_serializer.is_valid():
            file_serializer.save()
            if file_serializer.data['saved'] == 'Saved':
                return Response(file_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(file_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
