# https://www.dataquest.io/blog/machine-learning-python/
# http://nbviewer.jupyter.org/gist/justmarkham/6d5c061ca5aee67c4316471f8c2ae976
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn import metrics
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import mean_squared_error
import json
from collections import OrderedDict



print("\n\n##############################################################")
print("### Load In Data")
print("##############################################################")
print("Loading Training")
training_data = np.load('train_rolm.npz')
X_train = training_data['X']
Y_train = training_data['Y_PD']
print Y_train

print("Loading Test")
testing_data = np.load('test_rolm.npz')
X_test = testing_data['X']
Y_test = testing_data['Y_PD']
print Y_test

print("Loading Columns")
#players = np.load('players.npz').item()
with open('columns.json') as data_file:    
    model_columns = json.load(data_file)



print("\n\n##############################################################")
print("### Print the shapes of both sets.")
print("##############################################################")
print("train: %s" % (','.join(map(str, X_train.shape))))
print("test: %s" % (','.join(map(str, X_test.shape))))



print("\n\n##############################################################")
print("### Fit the model to the training data.")
print("##############################################################")
# Initialize the model class.
model = LinearRegression()
model.fit(X_train, Y_train)
print(model)

print("\n\n##############################################################")
print("### predict class labels for the test set")
print("##############################################################")
predicted = model.predict(X_test)
print "Actual"
print Y_test
print "Predicted"
print predicted

print("\n\n##############################################################")
print("### generate class probabilities")
print("##############################################################")
#probs = model.predict_proba(test[columns])
#print probs

print("\n\n##############################################################")
print("### generate evaluation metrics")
print("##############################################################")
#accuracy_score =  metrics.accuracy_score(test[target], predicted)
#print accuracy_score
#print metrics.roc_auc_score(test[target], probs[:, 1])
#print("The accuracy is %s percent" % (round(accuracy_score * 100, 0)))

print("\n\n##############################################################")
print("### generate confusion metrics")
print("##############################################################")
#print metrics.confusion_matrix(test[target], predicted)
#print metrics.classification_report(test[target], predicted)


print("\n\n##############################################################")
print("### evaluate the model using 10-fold cross-validation")
print("##############################################################")
#scores = cross_val_score(LinearRegression(), dataset[columns], dataset[target], scoring='accuracy', cv=10)
#print scores
#print scores.mean()


print("\n\n##############################################################")
print("### print player coefficients")
print("##############################################################")
#for entry in list(zip(train[columns], np.transpose(model.coef_))):
i = 0
player_scores = {}
for entry in np.transpose(model.coef_):
    column_name = model_columns[str(i)]
    player_key = unicode.replace(column_name, 'Team_A_', '')
    player_key = unicode.replace(player_key, 'Team_B_', '')
    player_scores[player_key] = entry[0]
    i += 1

player_scores = OrderedDict(sorted(player_scores.items(), key=lambda kv: kv[1], reverse=True))

for k,v in player_scores.items():
#collections.OrderedDict(sorted(player_scores.items())).items():
    print "%-30s %-4.2f" % (k, v)

print("\n\n##############################################################")
print("### Compute error between our test predictions and the actual values")
print("##############################################################")
# Generate our predictions for the test set.
predictions = model.predict(X_test)

# Compute error between our test predictions and the actual values.
print(mean_squared_error(predictions, Y_test))

