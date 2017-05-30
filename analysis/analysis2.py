# https://www.dataquest.io/blog/machine-learning-python/
# http://nbviewer.jupyter.org/gist/justmarkham/6d5c061ca5aee67c4316471f8c2ae976
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


def main():

	print("\n\n##############################################################")
	print("### Load In Data")
	print("##############################################################")
	print("Loading Training")
	training_data = np.load('train_rolm.npz')
	X_train = training_data['X']
	Y_train_won = training_data['Y_WON']
	c, r = Y_train_won.shape
	Y_train_won = Y_train_won.reshape(c,)
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

	print("\n\n##############################################################")
	print("### Print the shapes of both sets.")
	print("##############################################################")
	print("train: %s" % (','.join(map(str, X_train.shape))))
	print("train Y WON: %s" % (','.join(map(str, Y_train_won.shape))))
	print("test: %s" % (','.join(map(str, X_test.shape))))
	print("test Y WON: %s" % (','.join(map(str, Y_test_won.shape))))

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
	    print "%-30s %-4.2f" % (k, v)

	print("\n\n##############################################################")
	print("### Compute error between our test predictions and the actual values")
	print("##############################################################")
	# Generate our predictions for the test set.
	predictions = model.predict(X_test)

	# Compute error between our test predictions and the actual values.
	print(mean_squared_error(predictions, Y_test_won))

	return player_scores

if __name__ == "__main__":

    player_scores = main()
    for k,v in player_scores.items():
	    print "%-30s %-4.2f" % (k, v)

