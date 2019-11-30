from flask_table import Table, Col

class PlayerProjectionTable(Table):
    stat = Col('Projected Stat')
    value = Col('Value')

class HistoricTable(Table):
    week = Col('Week Number')
    score = Col('Fantasy Score')

class LeaderTable(Table):
    name = Col('Player Name')
    score = Col('Average Fantasy Score')
