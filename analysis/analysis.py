# https://www.dataquest.io/blog/machine-learning-python/
import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir) 

from bbtb_site.settings import DATABASES
import mysql.connector as sql
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA


db_connection = sql.connect(host=DATABASES['default']['HOST'], database=DATABASES['default']['NAME'], user=DATABASES['default']['USER'])


players = pd.read_sql('SELECT CAST(p.first_name as CHAR(50)) as player_id, t.id as team_id, t.won as won FROM team_manager_team t INNER JOIN team_manager_team_players tp on t.id = tp.team_id INNER JOIN team_manager_player p on tp.player_id = p.id', con=db_connection)
teams = pd.read_sql('SELECT t.id as team_id, CASE WHEN t.won > 0 THEN 1 ELSE -1 END as won FROM team_manager_team t', con=db_connection)

#teams = pd.concat([teams.drop('player_id', 1), pd.get_dummies(teams, columns=['player_id'])], axis=1)
#print pd.concat([players.drop('player_id', 1), pd.get_dummies(players, columns=['player_id'])], axis=1)
## Pivot Players as Categorical
#teams = pd.get_dummies(teams)

players["value"] = 1
players =  pd.pivot_table(players, values="value", index=["team_id"], columns="player_id", fill_value=0)
#print(players)

print(players.columns)
print(teams.columns)
print(players.shape)

#print (players.join(teams, lsuffix='_caller', rsuffix='_other'))
teams  =  players.join(teams.set_index('team_id'))
print teams

# Make a histogram of all the ratings in the average_rating column.
#plt.hist(teams["won"])

# Show the plot.
#plt.show()
#print(teams[teams["score"] == 16])

kmeans_model = KMeans(n_clusters=5, random_state=1)

# Get only the numeric columns from games.
good_columns = teams._get_numeric_data()
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

columns = teams.columns.tolist()
# Filter the columns to remove ones we don't want.
columns = [c for c in columns if c not in ["team_id", "won"]]

# Store the variable we'll be predicting on.
target = "won"


# Import a convenience function to split the sets.
from sklearn.model_selection import train_test_split

# Generate the training set.  Set random_state to be able to replicate results.
train = teams.sample(frac=0.8, random_state=1)
# Select anything not in the training set and put it in the testing set.
test = teams.loc[~teams.index.isin(train.index)]
# Print the shapes of both sets.
print(train.shape)
print(test.shape)

# Import the linearregression model.
from sklearn.linear_model import LinearRegression

# Initialize the model class.
model = LinearRegression()
# Fit the model to the training data.
model.fit(train[columns], train[target])

print(model)


for entry in list(zip(model.coef_, train[columns])):
	print "%s: \t\t\t %s" % (entry[1], format((entry[0] * 100), 'f'))


# Import the scikit-learn function to compute error.
from sklearn.metrics import mean_squared_error

# Generate our predictions for the test set.
predictions = model.predict(test[columns])

# Compute error between our test predictions and the actual values.
print(mean_squared_error(predictions, test[target]))


