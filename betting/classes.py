from fuzzywuzzy import process, fuzz

# switches: SWITCH_SW[is_main]
HOME_TEAM_SW = {0: 'Home', 1: 'HomeTeam'}
AWAY_TEAM_SW = {0: 'Away', 1: 'AwayTeam'}
HOME_GOALS_SW = {0: 'HG', 1: 'FTHG'}
AWAY_GOALS_SW = {0: 'AG', 1: 'FTAG'}
P_H_W_O_SW = {0: 'PH', 1: 'PSH'}
P_D_O_SW = {0: 'PD', 1: 'PSD'}
P_A_W_O_SW = {0: 'PA', 1: 'PSA'}
RESULT_SW = {0: 'Res', 1: 'FTR'}
LEAGUE_SW = {0: 'League', 1: 'Div'}

WAS_HOME_WIN_SW = {'H': 1, 'D': 0, 'A': 0}
WAS_DRAW_SW = {'H': 0, 'D': 1, 'A': 0}


class Game:
    def __init__(self, stat, pred):
        self.statistics = stat
        self.prediction_info = pred


class Statistics:
    def __init__(self, stat_d, is_main):
        self.country = stat_d['Country']
        self.date = stat_d['Date']
        self.league = stat_d[LEAGUE_SW[is_main]]

        self.home_team = stat_d[HOME_TEAM_SW[is_main]]
        self.away_team = stat_d[AWAY_TEAM_SW[is_main]]

        self.home_goals = stat_d[HOME_GOALS_SW[is_main]]
        self.away_goals = stat_d[AWAY_GOALS_SW[is_main]]

        self.result_char = stat_d[RESULT_SW[is_main]]
        self.was_home_win = WAS_HOME_WIN_SW[self.result_char]
        self.was_draw = WAS_DRAW_SW[self.result_char]

        self.pinnacle_home_win_odds = stat_d[P_H_W_O_SW[is_main]]
        self.pinnacle_draw_odds = stat_d[P_D_O_SW[is_main]]
        self.pinnacle_away_win_odds = stat_d[P_A_W_O_SW[is_main]]

        self.market_max_home_win_odds = stat_d['MaxH']
        self.market_max_draw_odds = stat_d['MaxD']
        self.market_max_away_win_odds = stat_d['MaxA']

        self.market_avg_home_win_odds = stat_d['AvgH']
        self.market_avg_draw_odds = stat_d['AvgD']
        self.market_avg_away_win_odds = stat_d['AvgA']


class Prediction:
    def __init__(self, pred_d):
        self.date = pred_d['DATE']
        self.home_team = pred_d['HOME']
        self.away_team = pred_d['AWAY']

        self.expected_goal_difference = pred_d['EXPECTED GOAL DIFFERENCE']
        self.expected_goal_difference_neutral = pred_d['EXPECTED GOAL DIFFERENCE NEUTRAL']
        self.home_chance = pred_d['HOME TEAM CHANCE']
        self.draw_chance = pred_d['DRAW CHANCE']
        self.away_chance = pred_d['AWAY TEAM CHANCE']

        self.home_chance_neutral = pred_d['HOME TEAM CHANCE NEUTRAL']
        self.draw_chance_neutral = pred_d['DRAW CHANCE NEUTRAL']
        self.away_chance_neutral = pred_d['AWAY TEAM CHANCE NEUTRAL']

    def get_stat_match(self, home_stat_dict, away_stat_dict, date_stats_dict):
        pass


class Matcher:
    def __init__(self, stats, preds):
        self.stats = stats
        self.preds = preds

        self.home_to_stats = self.get_home_to_stats()
        self.away_to_stats = self.get_away_to_stats()
        self.date_to_stats = self.get_date_to_stats()

    def get_home_to_stats(self):
        home_teams = list(set([s.home_team for s in self.stats]))
        return {home: [s for s in self.stats if s.home_team == home] for home in home_teams}

    def get_away_to_stats(self):
        away_teams = list(set(s.away_team for s in self.stats))
        return {away: [s for s in self.stats if s.away_team == away] for away in away_teams}

    def get_date_to_stats(self):
        dates = list(set(p.date for p in self.preds))
        return {date: [s for s in self.stats if s.date == date] for date in dates}

    def get_matches(self):
        """
        generator for Statistics, Predication pairings
        100% accuracy (96.4% - 100% w/ 95% confidence) achieved (n=100)
        :return: Statistics, Prediction objects
        """
        for pred in self.preds:
            date_stats = self.date_to_stats[pred.date]
            home_matched_name = process.extractOne(pred.home_team, [s.home_team for s in date_stats],
                                                   scorer=fuzz.partial_ratio, score_cutoff=75)
            away_matched_name = process.extractOne(pred.away_team, [s.away_team for s in date_stats],
                                                   scorer=fuzz.partial_ratio, score_cutoff=75)

            if home_matched_name and away_matched_name:
                home_matched_name, away_matched_name = home_matched_name[0], away_matched_name[0]
            else:
                continue

            home_matched_stat = [s for s in self.home_to_stats[home_matched_name] if s.date == pred.date][0]
            away_matched_stat = [s for s in self.away_to_stats[away_matched_name] if s.date == pred.date][0]

            if home_matched_stat.home_team == away_matched_stat.home_team and \
                    home_matched_stat.away_team == away_matched_stat.away_team:
                yield home_matched_stat, pred
