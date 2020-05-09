import tweepy
import re
import csv
import sys
import os
import api_tokens
from pathlib import Path
from unidecode import unidecode


CSV_HEADINGS = ['DATE', 'HOME', 'AWAY', 'EXPECTED GOAL DIFFERENCE', 'EXPECTED GOAL DIFFERENCE NEUTRAL',
                'HOME TEAM CHANCE', 'DRAW CHANCE', 'AWAY TEAM CHANCE', 'HOME TEAM CHANCE NEUTRAL',
                'DRAW CHANCE NEUTRAL', 'AWAY TEAM CHANCE NEUTRAL']


auth = tweepy.OAuthHandler(api_tokens.CONSUMER_KEY, api_tokens.CONSUMER_SECRET)
auth.set_access_token(api_tokens.ACCESS_TOKEN, api_tokens.ACCESS_TOKEN_SECRET)

api = tweepy.API(auth)


def get_statuses():
    """
    use tweepy to retrieve all available prediction-statuses
    :return: list of status instances
    """
    statuses = list()

    for status in tweepy.Cursor(api.user_timeline, id=836104384366936066).items():
        if is_prediction(status):
            statuses.append(status)
        else:
            continue

    return statuses


def is_prediction(status):
    if status.in_reply_to_status_id:
        return 0

    r1 = '((?:(?:[0-1][0-9])|(?:[2][0-3])|(?:[0-9])):(?:[0-5][0-9])(?::[0-5][0-9])?(?:\\s?(?:am|AM|pm|PM))?)'
    rg = re.compile(r1, re.DOTALL)

    if rg.search(status.text):
        return 1
    else:
        return 0


def is_changed(line0):
    rg = re.compile('(CHANGED)', re.IGNORECASE | re.DOTALL)
    if rg.search(line0):
        return True
    else:
        return False


def process_statuses(statuses):
    """
    process each status into a dictionary which has keys the same as the csv column headings
    :param statuses: list of tweepy status instances
    :return: list of dictionaries
    """
    status_dicts = list()

    for status in statuses:
        status_dict = dict()

        text = status.text
        splittext = text.split('\n')

        if is_changed(splittext[0]):  # adjust if text's first line is "changed"
            b = 1
        else:
            b = 0

        try:
            homeaway = get_teams(splittext[0 + b])
            status_dict['HOME'] = homeaway[0]
            status_dict['AWAY'] = homeaway[1]

            split_line1 = splittext[1+b].split(' / ')
            status_dict['EXPECTED GOAL DIFFERENCE'] = split_line1[0]
            status_dict['EXPECTED GOAL DIFFERENCE NEUTRAL'] = split_line1[1]

            split_line2 = splittext[2+b].split()
            status_dict['HOME TEAM CHANCE'] = split_line2[1]
            status_dict['DRAW CHANCE'] = split_line2[3]
            status_dict['AWAY TEAM CHANCE'] = split_line2[5]

            split_line3 = splittext[3+b].split()
            status_dict['HOME TEAM CHANCE NEUTRAL'] = split_line3[1]
            status_dict['DRAW CHANCE NEUTRAL'] = split_line3[3]
            status_dict['AWAY TEAM CHANCE NEUTRAL'] = split_line3[5]

            for key, val in status_dict.items():
                status_dict[key] = unidecode(val)  # transliterate unicode characters

        except IndexError as e:
            print(e)
            continue

        status_dict['DATE'] = status.created_at.strftime('%d/%m/%Y')

        status_dicts.append(status_dict)

    return status_dicts


def get_teams(line0):
    re1 = '((?:(?:[0-1][0-9])|(?:[2][0-3])|(?:[0-9])):(?:[0-5][0-9])(?::[0-5][0-9])?(?:\\s?(?:am|AM|pm|PM))?)'  # time
    re2 = '(:)'  # Any Single Character 1
    re3 = '(\\s+)'  # White Space 1

    rg = re.compile(re1 + re2 + re3, re.IGNORECASE | re.DOTALL)
    homeaway = rg.sub('', line0).split('vs.')  # get rid of time in tweet text; split() reduces string to team names

    home = homeaway[0].strip()
    away = homeaway[1].strip()

    return home, away


def write_csv(status_dicts, filepath):
    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADINGS)
        writer.writeheader()
        for status in status_dicts:
            writer.writerow(status)


def main():
    path_arg = Path(sys.argv[1])

    if os.path.isdir(path_arg.parent):
        write_file = path_arg
    else:
        raise NotADirectoryError(os.path.pardir(sys.argv[1]))

    statuses = get_statuses()  # create list of all twitter statuses

    status_dicts = process_statuses(statuses)  # process into list of dicts

    write_csv(status_dicts, write_file)  # write dicts to csv


if __name__ == '__main__':
    main()
