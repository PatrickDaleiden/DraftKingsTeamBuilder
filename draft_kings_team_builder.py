import csv
from mip import Model, xsum, maximize, BINARY, CONTINUOUS, INTEGER


class Player:
    def __init__(self, position, name, salary, ppg, oprk):
        self.position = position
        self.name = name
        self.salary = salary
        self.ppg = ppg
        self.oprk = oprk


quarterbacks = []
running_backs = []
wide_receivers = []
tight_ends = []
defense_special_teams = []

with open('C:\\Users\\Patrick\\Documents\\Draft_Kings_Sample_Data\\DKSalaries_Jan18.csv', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        if row["Status"] != "H":
            continue
        ppg = float(row["AvgPointsPerGame"])
        salary = float(row["Salary"])
        oprk = int(row["OPRK"])
        if int(row["OPRK"]) <= 10:
            ppg *= 0.8
        elif int(row["OPRK"]) >= 23:
            ppg *= 1.2

        if row["Position"] == "QB":
            quarterbacks.append(Player(row["Position"], row["Name"], salary, ppg, oprk))
        elif row["Position"] == "RB":
            running_backs.append(Player(row["Position"], row["Name"], salary, ppg, oprk))
        elif row["Position"] == "WR":
            wide_receivers.append(Player(row["Position"], row["Name"], salary, ppg, oprk))
        elif row["Position"] == "TE":
            tight_ends.append(Player(row["Position"], row["Name"], salary, ppg, oprk))
        elif row["Position"] == "DST":
            defense_special_teams.append(Player(row["Position"], row["Name"], salary, ppg, oprk))

qb_start = 0
qb_end = len(quarterbacks)
rb_start = qb_end
rb_end = rb_start + len(running_backs)
wr_start = rb_end
wr_end = wr_start + len(wide_receivers)
te_start = wr_end
te_end = te_start + len(tight_ends)
dst_start = te_end
dst_end = dst_start + len(defense_special_teams)

players = quarterbacks + running_backs + wide_receivers + tight_ends + defense_special_teams

m = Model('draft_kings_team_builder')

player_picks = [m.add_var(var_type=BINARY, name="Player[{}]: Pos[{}]".format(player.name, player.position)) for player in quarterbacks + running_backs + wide_receivers + tight_ends + defense_special_teams]

flex_choices = [m.add_var(var_type=BINARY, name="FLEX_CHOICE[%d]" % i) for i in range(3)]

m.objective = maximize(xsum(player.ppg * player_picks[idx] for idx, player in enumerate(players)))

m += xsum(player_picks[idx] * player.salary for idx, player in enumerate(players)) <= 50000
m += xsum(player_picks[i] for i in range(qb_start, qb_end)) == 1
m += xsum(player_picks[i] for i in range(rb_start, rb_end)) == 3 - (flex_choices[1] + flex_choices[2])
m += xsum(player_picks[i] for i in range(wr_start, wr_end)) == 4 - (flex_choices[0] + flex_choices[2])
m += xsum(player_picks[i] for i in range(te_start, te_end)) == 2 - (flex_choices[0] + flex_choices[1])
m += xsum(player_picks[i] for i in range(dst_start, dst_end)) == 1

m += xsum(flex_choices[i] for i in range(3)) == 1

m.optimize()

if m.num_solutions:
    for i in range(len(player_picks)):
        if player_picks[i].x == 1:
            print(player_picks[i].name)
