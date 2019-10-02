CREATE TABLE IF NOT EXISTS player (
  playerID INT UNSIGNED NOT NULL AUTO_INCREMENT,
  age INT UNSIGNED NOT NULL DEFAULT 0,
  position VARCHAR(20) NOT NULL DEFAULT '',
  name VARCHAR(30) NOT NULL DEFAULT '',

  FOREIGN KEY (offenseID) REFERENCES offense(offenseId),

  primary key (playerID)
);

CREATE TABLE IF NOT EXISTS offense(
  offenseID INT UNSIGNED NOT NULL AUTO_INCREMENT,
  rushingYardsAverage DECIMAL (4, 1) NOT NULL DEFAULT 0.0,
  rushingScoresAverage DECIMAL (4, 1) NOT NULL DEFAULT 0.0,
  passingYardsAverage DECIMAL (4, 1) NOT NULL DEFAULT 0.0,
  passingScoresAverage DECIMAL (4, 1) NOT NULL DEFAULT 0.0,
  receivingYardsAverage DECIMAL (4, 1) NOT NULL DEFAULT 0.0,
  receivingScoresAverage DECIMAL (4, 1) NOT NULL DEFAULT 0.0,
  season INT NOT NULL DEFAULT 2019,

  primary key (offenseID)
)

CREATE TABLE IF NOT EXISTS game (
  gameID INT UNSIGNED NOT NULL AUTO_INCREMENT,
  passingYards INT UNSIGNED NOT NULL DEFAULT 0,
  rushingYards INT UNSIGNED NOT NULL DEFAULT 0,
  receivingYards INT UNSIGNED NOT NULL DEFAULT 0,
  receptions INT UNSIGNED NOT NULL DEFAULT 0,
  receivingTargets INT UNSIGNED NOT NULL DEFAULT 0,
  rushingAttempts INT UNSIGNED NOT NULL DEFAULT 0,
  rushingScores INT UNSIGNED NOT NULL DEFAULT 0,
  passingScores INT UNSIGNED NOT NULL DEFAULT 0,
  receivingScores INT UNSIGNED NOT NULL DEFAULT 0,
  fumblesLost INT UNSIGNED NOT NULL DEFAULT 0,
  interceptionsThrown INT UNSIGNED NOT NULL DEFAULT 0,
  specialTeamsScores INT UNSIGNED NOT NULL DEFAULT 0,

  sacks INT UNSIGNED NOT NULL DEFAULT 0,
  fumblesGained INT UNSIGNED NOT NULL DEFAULT 0,
  interceptionsGained INT UNSIGNED NOT NULL DEFAULT 0,
  pointsAllowed INT UNSIGNED NOT NULL DEFAULT 0,
  rushingYardsAllowed INT NOT NULL DEFAULT 0,
  passingYardsAllowed INT NOT NULL DEFAULT 0,
  defensiveTouchdowns INT NOT NULL DEFAULT 0,
  defensiveSafeties INT NOT NULL DEFAULT 0,

  fieldGoalsMade INT UNSIGNED NOT NULL DEFAULT 0,
  fieldGoalsMissed INT UNSIGNED NOT NULL DEFAULT 0,
  extraPointsMade INT UNSIGNED NOT NULL DEFAULT 0,
  extraPointsMissed INT UNSIGNED NOT NULL DEFAULT 0,

  season INT NOT NULL DEFAULT 2019,

  FOREIGN KEY (playerID) REFERENCES player(playerID),
  FOREIGN KEY (opponentID) REFERENCES player(playerID),

  primary key (gameId)
)
