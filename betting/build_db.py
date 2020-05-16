from classes import Game, Statistics, Prediction, Matcher
import argparse
import os
import csv
from datetime import datetime  # TODO: REMOVE


MAIN_COUNTRIES = ['England', 'Scotland', 'Germany', 'Italy', 'Spain', 'France', 'Netherlands', 'Belgium', 'Portugal',
                  'Turkey', 'Greece']


def read_statistics(filepath):
    """
    create statistic objects by reading from .csv file
    :filepath: string, path to a csv
    :return: list of Statistics objects
    """
    file_stats = list()
    country_name = os.path.basename(os.path.dirname(filepath))

    if country_name in MAIN_COUNTRIES:
        is_main = True
    else:
        is_main = False

    with open(filepath, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row.update({'Country': country_name})
            try:
                file_stats.append(Statistics(row, is_main))
            except KeyError:
                continue  # rarely, a keyerror can result from erroneous data entering in spreadsheet

    return file_stats


def create_stats_list(basedir):
    """
    create list of all statistics objects by walking all game dirs
    :param basedir: base directory of statistics directories
    :return: list of Statistics objects
    """
    stats = list()

    for root, dirs, files in os.walk(basedir):
        for file in files:
            file_stats = read_statistics(os.path.join(root, file))
            for stat in file_stats:
                stats.append(stat)

    return stats


def create_preds_list(filepath):
    """
    create predictions objects by reading from .csv
    :param filepath: string, path to a csv
    :return: list of Predictions objects
    """
    preds = list()

    with open(filepath, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            preds.append(Prediction(row))

    return preds


def create_games_list(stats, preds):
    m = Matcher(stats, preds)

    return [Game(stat, pred) for stat, pred in m.get_matches()]


def get_args():
    parser = argparse.ArgumentParser(description='Use statistic and prediction files to generate a database in which'
                                                 'they are matched.')
    parser.add_argument('statistics_filepath', help='Absolute path to base directory of the output of '
                                                    'scrape_results.py')
    parser.add_argument('predictions_filepath', help='Absolute path to the file output of scrape_predictions.py')

    args = parser.parse_args()

    if not os.path.isdir(args.statistics_filepath):
        raise NotADirectoryError("First argument 'statistics_filepath' must be path to matches directory")
    if not os.path.exists(args.predictions_filepath):
        raise FileNotFoundError("Second argument must be path to prediction file")

    return args.statistics_filepath, args.predictions_filepath


def main():
    start = datetime.now()  # TODO: REMOVE

    stats_fp, preds_fp = get_args()

    stats = create_stats_list(stats_fp)
    print("stats: ", len(stats))

    preds = create_preds_list(preds_fp)
    print("preds: ", len(preds))

    games = create_games_list(stats, preds)

    # TODO: REMOVE
    end = datetime.now()
    print('Duration: {}'.format(end - start))

    print("games: ", len(games))
    for game in games:
        print("\n\n----GAME----")
        print('stats: ', game.statistics.date, game.statistics.home_team, '-', game.statistics.away_team)
        print('pred: ', game.prediction_info.date, game.prediction_info.home_team, '-', game.prediction_info.away_team)


if __name__ == '__main__':
    main()
