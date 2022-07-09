#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd
import tensorflow as tf
import numpy as np
from sklearn.model_selection import train_test_split


# In[4]:


class NeuralCore:
    def __init__(self,x,y,features,test_size=0.3,model=1,hidden_units=[10,10,10],
                n_classes=2):
        self.hidden_units = hidden_units
        self.n_classes = n_classes
        
        # Currently only works with pandas input functions and numeric columns
        self.x = x
        self.y = y
        
        #Split into training and testing sets
        self.x_train, self.x_test, self.y_train, self.y_test = train_test_split(self.x,self.y,test_size=test_size)
        
        # Constructs a tesnorflow features list
        self.feature_columns = []
        for feature in features:
            self.feature_columns.append(tf.feature_column.numeric_column(feature))
        
        self.set_model(model=model)
    
    def set_model(self,model):
        # DNN Classifier
        if model == 1:
            self.model = tf.estimator.DNNClassifier(feature_columns=self.feature_columns,n_classes=self.n_classes,
                                                   hidden_units=self.hidden_units)
        # Linear Classifier
        if model == 2:
            self.model = tf.estimator.LinearClassifier(feature_columns=self.feature_columns,n_classes=self.n_classes)
    
    def train(self,batch_size=1,num_epochs=1000,shuffle=True,steps=1000):
        self.shuffle = shuffle
        self.num_epochs = num_epochs
        self.steps = steps
        self.batch_size = batch_size
        
        # Creates input function
        train_input_fn = tf.estimator.inputs.pandas_input_fn(x=self.x_train,y=self.y_train,num_epochs=num_epochs,
                                                            shuffle=shuffle,batch_size=batch_size)
        self.model.train(input_fn=train_input_fn,steps=steps)
    
    def evaluate(self):
        eval_input_fn = tf.estimator.inputs.pandas_input_fn(x=self.x_train,y=self.y_train,num_epochs=1,
                                                            shuffle=False,batch_size=self.batch_size)
        results = self.model.evaluate(eval_input_fn)
        print(results)
    
    def predict(self,x_pred):
        # x_pred should be a pandas dataframe with same feature keys
        pred_input_fn = tf.estimator.inputs.pandas_input_fn(x=x_pred,num_epochs=1,
                                                            shuffle=False,batch_size=self.batch_size)
        preds = self.model.predict(pred_input_fn)
        return list(preds)


# In[ ]:




