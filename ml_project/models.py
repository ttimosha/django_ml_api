import os
from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import User

# Create your models here.

class UploadedFile(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=50, unique=True, editable=False)
    file = models.FileField(upload_to='files/')

    def __str__(self):
        return self.name

@receiver(models.signals.post_delete, sender=UploadedFile)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)

class Dataset(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE,)
    name = models.CharField(max_length=50)
    data = models.JSONField()
    uploadedFile = models.ForeignKey(UploadedFile, on_delete = models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class MLModel(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, default='test_model')
    train_dataset = models.ForeignKey(Dataset, on_delete = models.SET_NULL, editable=False, null=True)
    sklearn_pkl = models.FileField(upload_to='sklearn_models/')
    scores = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name