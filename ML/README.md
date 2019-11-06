# FF Prediction Models
    CWRU EECS 395 - Senior Project

    Michael Tucci
    michael-tucci@case.edu

## Requirments:
    pandas
    numpy
    sklearn
    sqlalchemy
    Keras
    matplotlib
    
## Notes:
    [10/17/2019]
           Initial setup w/pipenv.
           
           First goal is to write functions to pull and format data from AWS DB to build
           training datasets.
           
    [10/24/2019]
            Researched best practices w/LSTM and considered how to setup DataBuilder 
            accordingly.
            
            Commits:
                - Abstracted MySQL engine and queries. Engine initialized at object init.
                - Function to fetch "global" (all data in DB) min and max bounds for
                  each attribute in game and player tables. Will allow for normalization
                  of training data with respect to all data.
                - Manually drop unfilled (0's) attributes, remaining:
                    ['gameID', 'passingYards', 'rushingYards', 'receivingYards',
                   'receptions', 'receivingTargets', 'rushingAttempts', 'rushingScores',
                   'passingScores', 'receivingScores', 'fumblesLost',
                   'interceptionsThrown', 'season', 'playerID', 'opponentTeamID',
                   'ageDuringGame', 'weekNumber', 'passingCompletions', 'passingAttempts']
                - "Wiggle" normalization: extends min/max values for attribute data then
                  normalizes to [0,1]. Idea is to allow the network to guess below data
                  min or above data max.       
            
            Next:
                - Method to format DataFrame into time-series training set.
            
    [10/27/2019]
            Added better query methods and wrote method to convert DataFrame into training
            data set.
            
            Commits:
                - Methods to get all or limited player stats from game table sorted by
                  'season', 'then weekNumber', then 'gameID'. This gives correct ordering.
                - Method to build training data from DataFrame by either standard numpy
                  reshape or by "sliding" across the DataFrame to get more training samples.
                  
            Next:
                - Fix sliding method. Quick graphing methods.
                
    [11/1/2019]
            Small fixes to DataBuilder, added method for adding "0 weeks", and inital LSTM 
            tests.
            
            Commits:
                - Fixed data sliding
                - Added train/test split for time series builder
                - Added method to add "0 weeks" since there are no db entries if a player is
                  injured or otherwise doesn't register a stat during a week. Ideally this
                  will allow models to infer when a player is injured and make better 
                  predictions.
                - Optimizations
                
            Next:
                - Models and graphs
                
    [11/6/2019]
            Had to go back and make fixes to DataBuilder methods
            
            Commits:
                - Fix normalization to account for 0 opponentTeamID's from 0Weeks method.
                  Now picks a random ID. Will revisit and change this if neccessary. Likely
                  will remove opponentTeamID from input.
                - Added sorting to queries, created problem when not fetching all entries.
                - Setup series training data method properly.
                - Added __init__.py so I can import local modules.
            
            Next:
                - Models and graphs
    
    
    
