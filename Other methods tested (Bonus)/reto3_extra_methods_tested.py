# -*- coding: utf-8 -*-
"""reto3.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1jDmUGXcOxnLEkUdqbm_6-2_Hcg-QRq7j

# **INIT NOTEBOOK**
"""

#from google.colab import drive
#drive.mount('/content/drive')

# Commented out IPython magic to ensure Python compatibility.
# %cd /content/drive/My Drive/Colab Notebooks/reto3

#!ls

# Commented out IPython magic to ensure Python compatibility.
import sklearn
import numpy as np
import pandas as pd
import seaborn as sb

# %matplotlib inline
from matplotlib import pyplot as plt

from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.decomposition import PCA, KernelPCA
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import MinMaxScaler, StandardScaler

"""# **LOAD DATA** and show."""

trainset = pd.read_csv('../Datasets/reto3_trainX.csv')
labelset = pd.read_csv('../Datasets/reto3_trainY.csv')
names = trainset.columns

print(trainset.shape)
print(labelset.shape)

trainset.head()
#labelset.head()

all_dataset = trainset.copy()
all_dataset['tipo_bosque'] = labelset

plt.bar(all_dataset['tipo_bosque'].unique(),all_dataset['tipo_bosque'].value_counts(normalize=True,sort=False))

"""# **PRE-PROCEADODO**

Separar el dataset en Train y Test.

Normalizacion/escalado de los datos y/o reduccion de dimensiones con PCA.
"""

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(trainset, labelset, train_size=0.80, test_size=0.20, random_state=101)


# Elegir MinMaxScaler o StandardScaler en la variable use para aplicar uno de estos escalados.
use = 'MinMaxScaler'
error = False

if use=='MinMaxScaler':
    scaler = MinMaxScaler()
elif use=='StandardScaler':
    scaler = StandardScaler()
else:
    print("Error en el algoritmo elegido.")
    error=True

if error==False:  
    X_train_norm = scaler.fit_transform(X_train)
    X_test_norm = scaler.transform(X_test)
    y_train = y_train.values.ravel()
    y_test = y_test.values.ravel()
    print(X_train_norm.shape)
    print(y_train.shape)

# PCA -> reduccion de dimensionalidad a n_components.
n_components = 15 
kernel = "sigmoid" # options are: "linear", "poly", "rbf", "sigmoid"
kernel_parameter = 1

pca = PCA(n_components = n_components)
X_train_proy = pca.fit_transform(X_train_norm)
X_test_proy = pca.transform(X_test_norm)

#Show all components on pairplot.
show_proy = pd.DataFrame(X_train_proy)
show_proy['tipo_bosque'] = y_train
sb.pairplot(show_proy, hue='tipo_bosque')

"""# **RANDOM FOREST**
Busqueda de caracteristitcas con mas relevancia.
"""
# Funcion para entrenar varios RF con diferentes hiperparametros y quedarnos con el mejor.

def TryParamsRF(x_data,y_data,param_grid=None):
    if param_grid==None:
        param_grid = {'n_estimators': [100, 150, 200, 250], 'max_depth': [1, 2], 'criterion': ['gini', 'entropy'], 'max_features': ['auto', 'sqrt', 'log2']}

    forest = RandomForestClassifier(random_state=0,verbose=0)
    forest_grid = GridSearchCV(forest,param_grid,refit=True,verbose=2)
    forest_grid.fit(x_data,y_data)
    return forest_grid

## Ejecutar celda para entrenar un RF con parametros fijos o probar diferentes configuraciones.
# 0=train con parametros fijos || 1=train con prueba de diferentes parametros.
find_best_model = 0  

if find_best_model==1:
    #param_grid = {'n_estimators': [250], 'max_depth': [2], 'criterion': ['gini'], 'max_features': ['auto']}
    param_grid = {'n_estimators': [100, 150, 200, 250], 'max_depth': [1, 2], 'criterion': ['gini', 'entropy'], 'max_features': ['auto', 'sqrt', 'log2']}
    forest_grid = TryParamsRF(X_proy,y_train,param_grid=param_grid)
    n_estimators = forest_grid.best_estimator_.n_estimators
    max_depth = forest_grid.best_estimator_.max_depth
    criterion = forest_grid.best_estimator_.criterion
    max_features = forest_grid.best_estimator_.max_features
    print(forest_grid.best_estimator_)

else:
    n_estimators = 200
    max_depth = 12
    criterion = 'gini'
    max_features = 'auto'

forest = RandomForestClassifier(random_state=0,
                                verbose=0,
                                n_estimators=n_estimators,
                                max_depth=max_depth,
                                criterion=criterion,
                                max_features=max_features)

forest.fit(X_train_proy,y_train)
importances = forest.feature_importances_

predictions = forest.predict(X_test_proy)
print(confusion_matrix(y_test,predictions))
print(classification_report(y_test,predictions))

"""Representación de las caracteristicas obtenidas de mas importancia.

Utilizamos un umbral para quedarnos con las relevantes y las guardamos un en nuevo dataset que realizaremos de nuevo el pre-procesador.
"""

flt = (importances > 0.01)

new_importances = importances[flt]
new_names = names[flt]
trainset_v2 = trainset[new_names].copy()
plt.barh(names[flt], importances[flt])

from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(trainset_v2, labelset, train_size=0.80, test_size=0.20, random_state=101)

scaler = MinMaxScaler()
X_train_norm = scaler.fit_transform(X_train)
X_test_norm = scaler.transform(X_test)
y_train = y_train.values.ravel()
y_test = y_test.values.ravel()

"""# **SVC**  
#### **(SUPPORT VECTOR MACHINE CLASSIFIER)**
"""

# Funcion para entrenar varios SVC con diferentes hiperparametros y quedarnos con el mejor.
def TryParamsSVC(x_data, y_data, params_grid=None):

    if params_grid==None:
        param_grid = {'C': [0.1, 1, 10, 100], 'degree': [2, 3, 4, 5], 'gamma': [1, 0.1, 0.01, 0.001], 'kernel': ['rbf', 'sigmoid','poly']}

    model = SVC()
    grid = GridSearchCV(model,param_grid,refit=True,verbose=2)
    grid.fit(X_train,y_train)
    return grid

## Ejecutar celda para entrenar un RF con parametros fijos o probar diferentes configuraciones.

# 0=train con parametros fijos || 1=train con prueba de diferentes parametros.
find_best_model = 0

if find_best_model==1:
    param_grid = {'C': [0.1, 1, 10, 100], 'gamma': [0.01, 0.001], 'kernel': ['rbf', 'sigmoid']}
    TryParamsSVC(X_train_norm,y_train,params_grids)
    c = grid.best_estimator_.c
    gamma = grid.best_estimator_.gamma
    kernel = grid.best_estimator_.kernel
    degree = grid.best_estimator_.degree

else: #Manual inputs of parameters.
    c = 0.1
    gamma = 'auto'
    kernel = 'sigmoid'
    degree = 3 #-> Ignored if kernel is not a Poly.

model = SVC(random_state=0, verbose=2, kernel=kernel, C=c, gamma=gamma, degree=degree)
model.fit(X_train_proy,y_train)

predictions = model.predict(X_test_proy)
print(confusion_matrix(y_test,predictions))
print(classification_report(y_test,predictions))



"""# **ADA BOOST CLASSIFIER**"""

n_estimators = 100
lr = 0.15

ABC = AdaBoostClassifier(n_estimators=n_estimators, random_state=0)
ABC.fit(X_train_proy, y_train)

predictions = ABC.predict(X_test_proy)
print(confusion_matrix(y_test,predictions))
print(classification_report(y_test,predictions))



"""# **DECISION TREE CLASSIFIER**"""

max_depth = 15

DT = DecisionTreeClassifier(random_state=0, max_depth=max_depth)
DT.fit(X_train_proy, y_train)

predictions = DT.predict(X_test_proy)
print(confusion_matrix(y_test,predictions))
print(classification_report(y_test,predictions))



"""# **Gradient Boosting Classifier**"""

n_estimators = 100
lr = 0.08

GBC = GradientBoostingClassifier(learning_rate=lr, n_estimators=n_estimators)
GBC.fit(X_train_norm, y_train)

predictions = GBC.predict(X_test_norm)
print(confusion_matrix(y_test,predictions))
print(classification_report(y_test,predictions))



"""# **SAVE MODEL USING PICKLE**"""

import pickle
from datetime import datetime

now = datetime.now()
date = now.strftime("%d/%m/_%H:%M:%S")

filename = 'models/SVC_'
path_file = filename+date+'.sav'

pickle.dump(model, open(path_file, 'wb'))

