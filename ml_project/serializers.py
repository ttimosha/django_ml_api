from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Dataset, MLModel, UploadedFile
from .functions import create_dataset_instance, create_model
from django.db.utils import IntegrityError


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ('id', 'username',)

class DatasetSerializer(serializers.ModelSerializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    name = serializers.ReadOnlyField()
    data = serializers.ReadOnlyField()
    class Meta:
        model = Dataset
        fields = ('id', 'creator', 'name', 'data', 'created_at', 'updated_at')

class MLModelSerializer(serializers.ModelSerializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = MLModel
        fields = ('id', 'creator', 'train_dataset', 'sklearn_pkl', 'scores', 'created_at', 'updated_at')
    
class LoadDatasetSerializer(serializers.Serializer):
    file = serializers.FileField()
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    #name = serializers.CharField(max_length=50)
    name = serializers.HiddenField(default='')

    def create(self, validated_data):
        file_name = validated_data['file'].name
        # django removes ' ' from file names
        file_name = file_name.replace(' ', '_')
        # even if unique is set to True, django creates new file with unique name
        if UploadedFile.objects.filter(name = file_name).count():
            self.name = file_name
            raise IntegrityError

        uploadedFile = UploadedFile.objects.create(
            name = file_name, 
            creator = validated_data['creator'], 
            file = validated_data['file']
            )

        create_dataset_instance(uploadedFile)
        return uploadedFile

class ResultSerializer(serializers.Serializer):
    scores = serializers.JSONField()

class CreateModelSerializer(serializers.Serializer):
    model_type = serializers.ChoiceField(choices=['regression', 'classification'])
    model = serializers.ChoiceField(choices=['Linear', 'Gradient Boosting', 'Random Forest'])
    normalize = serializers.ChoiceField(choices=['No scaler', 'Standard Scaler'])
    encode_categorical = serializers.ChoiceField(choices=['No encoding', 'Label Encoder', 'Dummy Encoder'])
    save_model = serializers.ChoiceField(choices=[False, True])
    train_test_split = serializers.ChoiceField(choices=[True, False])
    y_name = serializers.CharField(max_length=50)
    name = serializers.CharField(max_length=50)
    scores = serializers.ReadOnlyField(default={})
    saved = serializers.ReadOnlyField(default = 'Not saved')

    def __init__(self, *args, **kwargs):
        user = kwargs['context']['request'].user

        super(CreateModelSerializer, self).__init__(*args, **kwargs)
        self.fields['dataset'] = serializers.PrimaryKeyRelatedField(queryset=Dataset.objects.filter(creator = user))

    def create(self, validated_data):
        result = create_model(
            validated_data = validated_data,
            creator = self.context['request'].user
        )
    

        return result
