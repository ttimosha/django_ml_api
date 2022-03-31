from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import UserViewSet, DatasetViewSet, MLModelViewSet, UploadFileView, CreateModelView

router = SimpleRouter()
router.register('users', UserViewSet, basename='users')
router.register('datasets', DatasetViewSet, basename='datasets')
router.register('models', MLModelViewSet, basename='models')
router.register('upload_file', UploadFileView, basename='files')

urlpatterns = [
    path('create_model/', CreateModelView.as_view()),
    path('', include(router.urls)),
]