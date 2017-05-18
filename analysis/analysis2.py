# https://www.dataquest.io/blog/machine-learning-python/
# http://nbviewer.jupyter.org/gist/justmarkham/6d5c061ca5aee67c4316471f8c2ae976
import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir) 

from bbtb_site.settings import DATABASES
import mysql.connector as sql
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


db_connection = sql.connect(host=DATABASES['default']['HOST'], database=DATABASES['default']['NAME'], user=DATABASES['default']['USER'])


players_won = pd.read_sql("SELECT CAST(p.first_name as CHAR(50)) as player_id, t.id as team_id, gt.game_id, t.won as won FROM team_manager_team t INNER JOIN team_manager_team_players tp on t.id = tp.team_id INNER JOIN team_manager_player p on tp.player_id = p.id INNER JOIN team_manager_game_teams gt on gt.team_id = t.id WHERE t.name = 'Team A'", con=db_connection)
players_lost= pd.read_sql("SELECT CAST(p.first_name as CHAR(50)) as player_id, t.id as team_id, gt.game_id, t.won as won FROM team_manager_team t INNER JOIN team_manager_team_players tp on t.id = tp.team_id INNER JOIN team_manager_player p on tp.player_id = p.id INNER JOIN team_manager_game_teams gt on gt.team_id = t.id WHERE t.name = 'Team B'", con=db_connection)
team_a_results = pd.read_sql("SELECT t.won, t.point_differential, gt.game_id  from team_manager_team t INNER JOIN team_manager_game_teams gt ON t.id = gt.team_id WHERE t.name = 'Team A'", con=db_connection)

players_won["value"] = 1
players_won =  pd.pivot_table(players_won, values="value", index=["game_id"], columns="player_id", fill_value=0)

players_lost["value"] = 1
players_lost =  pd.pivot_table(players_lost, values="value", index=["game_id"], columns="player_id", fill_value=0)


dataset = players_won.join(players_lost, lsuffix='_team_a', rsuffix='_team_b')
dataset  =  dataset.join(team_a_results.set_index('game_id'))

#print dataset

# Make a histogram of all the ratings in the average_rating column.
#plt.hist(dataset["point_differential"])

# Show the plot.
#plt.show()
#print(teams[teams["score"] == 16])

kmeans_model = KMeans(n_clusters=5, random_state=1)

# Get only the numeric columns from games.
good_columns = dataset._get_numeric_data()
# Fit the model using the good columns.
kmeans_model.fit(good_columns)
# Get the cluster assignments.
labels = kmeans_model.labels_

# Create a PCA model.
pca_2 = PCA(2)
# Fit the PCA model on the numeric columns from earlier.
plot_columns = pca_2.fit_transform(good_columns)
# Make a scatter plot of each game, shaded according to cluster assignment.
plt.scatter(x=plot_columns[:,0], y=plot_columns[:,1], c=labels)
# Show the plot.
#plt.show()

#print(teams.corr()["point_differential"])

columns = dataset.columns.tolist()
# Filter the columns to remove ones we don't want.
columns = [c for c in columns if c not in ["game_id", "won", "point_differential"]]

# Store the variable we'll be predicting on.
target = "won"


### Import a convenience function to split the sets.
from sklearn.model_selection import train_test_split

#### Generate the training set.  Set random_state to be able to replicate results.
train = dataset.sample(frac=0.8, random_state=1)
#### Select anything not in the training set and put it in the testing set.
test = dataset.loc[~dataset.index.isin(train.index)]


print("\n\n##############################################################")
print("### Print the shapes of both sets.")
print("##############################################################")
print("train: %s" % (','.join(map(str, train.shape))))
print("test: %s" % (','.join(map(str, test.shape))))



print("\n\n##############################################################")
print("### Fit the model to the training data.")
print("##############################################################")
# Initialize the model class.
model = LogisticRegression()
model.fit(train[columns], train[target])
print(model)

print("\n\n##############################################################")
print("### predict class labels for the test set")
print("##############################################################")
predicted = model.predict(test[columns])
print "Actual"
print test[target]
print "Predicted"
print predicted

print("\n\n##############################################################")
print("### generate class probabilities")
print("##############################################################")
probs = model.predict_proba(test[columns])
print probs

print("\n\n##############################################################")
print("### generate evaluation metrics")
print("##############################################################")
accuracy_score =  metrics.accuracy_score(test[target], predicted)
print accuracy_score
print metrics.roc_auc_score(test[target], probs[:, 1])
print("The accuracy is %s percent" % (round(accuracy_score * 100, 0)))

print("\n\n##############################################################")
print("### generate confusion metrics")
print("##############################################################")
print metrics.confusion_matrix(test[target], predicted)
print metrics.classification_report(test[target], predicted)


print("\n\n##############################################################")
print("### evaluate the model using 10-fold cross-validation")
print("##############################################################")
scores = cross_val_score(LogisticRegression(), dataset[columns], dataset[target], scoring='accuracy', cv=10)
print scores
print scores.mean()


#print(model)
#print model.coef_


print("\n\n##############################################################")
print("### print player coefficients")
print("##############################################################")
for entry in list(zip(train[columns], np.transpose(model.coef_))):
    print "%s: \t\t\t %s" % (entry[0], entry[1][0])


print("\n\n##############################################################")
print("### predict the trobability of a win")
print("##############################################################")
print("### Stacked Positive Team")
good_team = np.array([0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,1,1,1,1,0,0,1,1,0,0,0,0,1,0,0,0,0,1,0,0,0])
print model.predict_proba(good_team.reshape(1, -1))
print("### Stacked Negative Team")
bad_team = np.array([1,0,0,1,0,0,0,0,0,1,0,0,0,1,1,0,0,0,0,0,1,0,0,0,1,0,0,0,0,1,0,0,0,1,1,0])
print model.predict_proba(bad_team.reshape(1, -1))


# Import the scikit-learn function to compute error.
from sklearn.metrics import mean_squared_error

# Generate our predictions for the test set.
predictions = model.predict(test[columns])

# Compute error between our test predictions and the actual values.
#print(mean_squared_error(predictions, test[target]))


