from django.contrib import admin
from .models import MLModel, Dataset, UploadedFile

# Register your models here.
admin.site.register(MLModel)
admin.site.register(Dataset)
admin.site.register(UploadedFile)