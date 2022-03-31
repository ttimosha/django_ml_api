from django.conf import settings
import os
import pickle
import uuid
import pandas as pd
import numpy as np
from django.core.files import File
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor, RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error, accuracy_score, f1_score
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split as tt_split
from .models import Dataset, MLModel
import json


def create_dataset_instance(uploadedFile):
    name = uploadedFile.name
    file_type = name.split('.')[-1]
    df = pandas_file_types[file_type](os.path.join(settings.BASE_DIR, f'files\\{name}'))
    json = df.to_json()
    dataset = Dataset.objects.create(creator = uploadedFile.creator, 
                                     name = uploadedFile.name,
                                     data = json, 
                                     uploadedFile = uploadedFile)
    return dataset

def create_model(validated_data, creator):
    model_type = validated_data['model_type']
    model = validated_data['model']
    dataset= validated_data['dataset']
    y_name = validated_data['y_name']

    dataset_instance = Dataset.objects.get(id = dataset.id)
    _json = json.loads(dataset_instance.data)
    df = pd.DataFrame(_json)
    sklearn_model = sklearn_models[model_type][model]()
    pipeline = Pipeline(steps=[('estimator', sklearn_model)])

    if df.isnull().sum().sum() > 0:
        df = fill_null_values(df)
    
    if validated_data['encode_categorical'] == 'Label Encoder':
        df = label_encode(df)
    elif validated_data['encode_categorical'] == 'Dummy Encoder':
        df = pd.get_dummies(df)

    if validated_data['normalize'] == 'Standard Scaler':
        pipeline.steps.insert(0, ('preprocessor', StandardScaler()))

    x, y = df.drop([y_name], axis = 1), df[y_name]

    if validated_data['train_test_split']:
        X_train, X_test, y_train, y_test = tt_split(x, y)
        pipeline.fit(X_train, y_train)
    else:
        pipeline.fit(x, y)
        X_test, y_test = x, y #сделать загрузку для тест датасета

    model_pred = pipeline.predict(X_test)

    if model_type == 'regression':
        mae = '{:.4f}'.format(mean_absolute_error(y_test, model_pred))
        rmse = '{:.4f}'.format(np.sqrt(mean_squared_error(y_test, model_pred)))
        r2 = '{:.4f}'.format(r2_score(y_test, model_pred))
        result = {'mae': mae, 'rmse': rmse, 'r2': r2}
    elif model_type == 'classification':
        acc = '{:.4f}'.format(accuracy_score(y_test, model_pred))
        f1 = '{:.4f}'.format(f1_score(y_test, model_pred))
        result = {'accuracy_score': acc, 'f1': f1}

    if validated_data['save_model']:
        file_name = str(uuid.uuid4())  
        file_path = 'temporary_files/' +  file_name
        with open(file_path, 'wb') as file:
            pickle.dump(pipeline, file)
        with open(file_path, 'rb') as file:
            MLModel.objects.create(
                    creator = creator,
                    name = validated_data['name'],
                    train_dataset = dataset,
                    sklearn_pkl = File(file, name = file_name),
                    scores = result
                )
        os.remove(os.path.join(settings.BASE_DIR, file_path))
        saved = 'Saved'
    else:
        saved = 'Not saved'
        print(result)
    
    validated_data['scores'] = result
    validated_data['saved'] = saved
    return validated_data

def fill_null_values(df):
    cat_cols = [c for c in df.columns if df[c].dtype.name == 'object']
    num_cols = [c for c in df.columns if df[c].dtype.name != 'object']

    for col in cat_cols:
        frequent = df[col].mode()[0]
        df[col].fillna(frequent, inplace = True)

    for col in num_cols:
        median_value = df[col].median()
        df[col].fillna(median_value, inplace = True)

    return df

def label_encode(df):
    cat_cols = [c for c in df.columns if df[c].dtype.name == 'object']

    for col in cat_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])

    return df

pandas_file_types = {
    'pkl': pd.read_pickle,
    'csv': pd.read_csv,
    'xls': pd.read_excel,
    'xlsx': pd.read_excel,
    'json': pd.read_json
}

sklearn_models = {
    'regression': {
        'Linear': LinearRegression,
        'Gradient Boosting': GradientBoostingRegressor,
        'Random Forest': RandomForestRegressor,
    },
    'classification':{
        'Linear': LogisticRegression,
        'Gradient Boosting': GradientBoostingClassifier,
        'Random Forest': RandomForestClassifier,
    },
}