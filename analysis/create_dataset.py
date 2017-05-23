import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir) 

from bbtb_site.settings import DATABASES
import mysql.connector as sql
import numpy as np
import json
from scipy import sparse
import collections


def create():

    db_connection = sql.connect(host=DATABASES['default']['HOST'], database=DATABASES['default']['NAME'], user=DATABASES['default']['USER'])
    cursor = db_connection.cursor()

    ### Get Players
    cursor.execute("SELECT id FROM team_manager_player")
    dict_players = {}
    player_id = 0
    for id in cursor:
        dict_players[player_id] = id[0]
        player_id += 1


    print dict_players


    ### Get Games
    array_games = []
    cursor.execute("SELECT id FROM team_manager_game")
    for (id) in cursor:
        array_games.append(id[0])

    ### Get Team A
    dict_teams_a = {}
    cursor.execute("SELECT p.id as player_id, t.id as team_id, gt.game_id, t.won, t.point_differential as won FROM team_manager_team t INNER JOIN team_manager_team_players tp on t.id = tp.team_id INNER JOIN team_manager_player p on tp.player_id = p.id INNER JOIN team_manager_game_teams gt on gt.team_id = t.id WHERE t.name = 'Team A'")
    for (teams) in cursor:
        team_id = teams[1]
        dict_teams_a[teams[1]] = {'game_id':teams[2], 'players': [], 'won': teams[3], 'point_differential': teams[4]}

    cursor.execute("SELECT p.id as player_id, t.id as team_id, gt.game_id, t.won, t.point_differential as won FROM team_manager_team t INNER JOIN team_manager_team_players tp on t.id = tp.team_id INNER JOIN team_manager_player p on tp.player_id = p.id INNER JOIN team_manager_game_teams gt on gt.team_id = t.id WHERE t.name = 'Team A'")
    for (teams) in cursor:
        player_id = next((k for k,player in dict_players.items() if player == teams[0]))
        dict_teams_a[teams[1]]['players'].append(player_id)

    ### Get Team B
    dict_teams_b = {}
    cursor.execute("SELECT p.id as player_id, t.id as team_id, gt.game_id, t.won as won FROM team_manager_team t INNER JOIN team_manager_team_players tp on t.id = tp.team_id INNER JOIN team_manager_player p on tp.player_id = p.id INNER JOIN team_manager_game_teams gt on gt.team_id = t.id WHERE t.name = 'Team A'")
    for (teams) in cursor:
        team_id = teams[1]
        dict_teams_b[teams[1]] = {'game_id':teams[2], 'players': []}

    cursor.execute("SELECT p.id as player_id, t.id as team_id, gt.game_id, t.won as won FROM team_manager_team t INNER JOIN team_manager_team_players tp on t.id = tp.team_id INNER JOIN team_manager_player p on tp.player_id = p.id INNER JOIN team_manager_game_teams gt on gt.team_id = t.id WHERE t.name = 'Team A'")
    for (teams) in cursor:
        player_id = next((k for k,player in dict_players.items() if player == teams[0]))
        dict_teams_b[teams[1]]['players'].append(player_id)

    # Initialize training matrix
    num_games = len(array_games)
    num_players = len(dict_players)
    num_features = num_players * 2
    print "NUM_HEROES=%s" % (num_players)
    print "NUM_FEATURES=%s" % (num_features)
    X = np.zeros((num_games, num_features), dtype=np.int32)

    # Initialize training label vector
    Y_WON = np.zeros((num_games, 1), dtype=np.int32)
    Y_PD = np.zeros((num_games, 1), dtype=np.int32)


    #Set Win/Loss Values
    i = 0
    for game in array_games:
        team_a = next((item for k,item in dict_teams_a.items() if item.get("game_id") == game))
        Y_WON[i] = team_a['won']
        Y_PD[i] = team_a['point_differential']
        i += 1

    #Set Team A Values
    i = 0
    for k,teams in dict_teams_a.items():
        for player in teams['players']:
            X[i, player] = 1
        i += 1

    #Set Team B Values
    i = 0
    for k,teams in dict_teams_b.items():
        for player in teams['players']:
            X[i, (player + num_players)] = 1 ## Need to Add Number Players to player ID for Team B
        i += 1


    print "Permuting, generating train and test sets."
    indices = np.random.permutation(num_games)
    test_indices = indices[0:num_games/5]
    train_indices = indices[num_games/5:num_games]

    X_test = X[test_indices]
    Y_test_won = Y_WON[test_indices]
    Y_test_pd = Y_PD[test_indices]


    X_train = X[train_indices]
    Y_train_won = Y_WON[train_indices]
    Y_train_pd = Y_PD[train_indices]

    print "Saving output files now..."
    columns = {}
    for k,player in dict_players.items():
        columns[k] = "Team_A_%s" % (player)

    for k,player in dict_players.items():
        columns[(k+len(dict_players))] = "Team_B_%s" % (player)

    with open('columns.json', 'w') as fout:
        json.dump(columns, fout)


    arr_columns = list(item for k,item in collections.OrderedDict(sorted(columns.items())).items())
    arr_columns.append("Won")
    arr_columns.insert(0, '')


    output = np.hstack((X,Y_WON)) 
    output_big = output

    i = 1
    total_rows  = 0
    while i < 10:
        output_big = np.vstack((output, output_big)) 
        total_rows = total_rows + output.shape[0]
        print "total rows: %s" % (total_rows)
        print "Appending %s iteration for %s total rows" % (i, output_big.shape)
        i+= 1

    print len(output_big)
    id = [i for i in xrange(1,len(output_big)+1)]

    output_big = np.insert(output_big, 0, id, axis=1)


    np.savetxt('full_rolm.csv', output_big, fmt='%d', delimiter=',', header = (",").join(arr_columns))
    np.savez_compressed('full_rolm.npz', X=X, Y_WON=Y_WON,  Y_PD=Y_PD)
    np.savez_compressed('test_rolm.npz', X=X_test, Y_WON=Y_test_won,  Y_PD=Y_test_pd)
    np.savez_compressed('train_rolm.npz', X=X_train, Y_WON=Y_train_won,  Y_PD=Y_train_pd)

if __name__ == "__main__":

    create()




