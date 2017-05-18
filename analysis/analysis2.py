# https://www.dataquest.io/blog/machine-learning-python/
# http://nbviewer.jupyter.org/gist/justmarkham/6d5c061ca5aee67c4316471f8c2ae976
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn import metrics
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import mean_squared_error
import json




print("\n\n##############################################################")
print("### Load In Data")
print("##############################################################")
print("Loading Training")
training_data = np.load('train_rolm.npz')
X_train = training_data['X']
Y_train_won = training_data['Y_WON']
print Y_train_won

print("Loading Test")
testing_data = np.load('test_rolm.npz')
X_test = testing_data['X']
Y_test_won = testing_data['Y_WON']
print Y_test_won

print("Loading Columns")
#players = np.load('players.npz').item()
with open('columns.json') as data_file:    
    model_columns = json.load(data_file)

# Make a histogram of all the ratings in the average_rating column.
#plt.hist(Y_train)
# Show the plot.
#plt.show()

print("\n\n##############################################################")
print("### Print the shapes of both sets.")
print("##############################################################")
print("train: %s" % (','.join(map(str, X_train.shape))))
print("test: %s" % (','.join(map(str, X_test.shape))))

print("\n\n##############################################################")
print("### Fit the model to the training data.")
print("##############################################################")
# Initialize the model class.
model = LogisticRegression()
model.fit(X_train, Y_train_won)
print(model)

print("\n\n##############################################################")
print("### predict class labels for the test set")
print("##############################################################")
predicted = model.predict(X_test)
print "Actual"
print Y_test_won
print "Predicted"
print predicted

print("\n\n##############################################################")
print("### generate class probabilities")
print("##############################################################")
probs = model.predict_proba(X_test)
print probs

print("\n\n##############################################################")
print("### generate evaluation metrics")
print("##############################################################")
accuracy_score =  metrics.accuracy_score(Y_test_won, predicted)
print accuracy_score
print metrics.roc_auc_score(Y_test_won, probs[:, 1])
print("The accuracy is %s percent" % (round(accuracy_score * 100, 0)))

print("\n\n##############################################################")
print("### generate confusion metrics")
print("##############################################################")
print metrics.confusion_matrix(Y_test_won, predicted)
print metrics.classification_report(Y_test_won, predicted)


print("\n\n##############################################################")
print("### evaluate the model using 10-fold cross-validation")
print("##############################################################")
scores = cross_val_score(LogisticRegression(), X_train, Y_train_won, scoring='accuracy', cv=10)
print scores
print scores.mean()


print("\n\n##############################################################")
print("### print player coefficients")
print("##############################################################")
#for entry in list(zip(train[columns], np.transpose(model.coef_))):
i = 0
for entry in np.transpose(model.coef_):
    print "%-30s %-4.2f" % (model_columns[str(i)], entry)
    i += 1

print("\n\n##############################################################")
print("### Compute error between our test predictions and the actual values")
print("##############################################################")
# Generate our predictions for the test set.
predictions = model.predict(X_test)

# Compute error between our test predictions and the actual values.
print(mean_squared_error(predictions, Y_test_won))


