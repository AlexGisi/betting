import requests
import bs4
import os
import sys


MAIN_COUNTRIES = ['England', 'Scotland', 'Germany', 'Italy', 'Spain', 'France', 'Netherlands', 'Belgium', 'Portugal',
                  'Turkey', 'Greece']
EXTRA_COUNTRIES = ['Austria', 'Brazil', 'Denmark', 'Finland', 'Mexico', 'Norway', 'Poland', 'Romania', 'Russia',
                   'Sweden', 'Switzerland', 'USA']
PARENT_URL = 'http://www.football-data.co.uk/country.php'


def download_pages(countries, is_main, base_dir):
    """

    :param countries:
    :param is_main: bool, true if main
    :param base_dir: str
    :return:
    """
    for country in countries:
        if is_main:
            url = 'http://www.football-data.co.uk/' + country + 'm' + '.php'
        else:
            url = 'http://www.football-data.co.uk/' + country + '.php'

        csv_res = requests.get(url)
        csv_res.raise_for_status()

        country_urls = get_csv_urls(csv_res)

        os.chdir(os.path.abspath(base_dir))

        if not os.path.exists(country):
            os.mkdir(country)

        for url in country_urls:
            csv_res = requests.get(url)  # download page
            csv_res.raise_for_status()

            if is_main:
                year = int(url.split('/')[4])
                if year == 1920:  # only get files from 2019-2020 season
                    file_name = url.split('/')[4] + '-' + url.split('/')[5]  # name according to division-year
                else:
                    continue
            else:
                file_name = url.split('/')[4]

            write_path = os.path.join(base_dir, country, file_name)
            with open(write_path, 'wb') as f:
                f.write(csv_res.content)

            print('Wrote file: ', file_name)


def get_csv_urls(response):
    """
    get csv files on a countries' page
    :param response:
    :return:
    """
    page_soup = bs4.BeautifulSoup(response.text, features="html.parser")
    page_urls = list()
    csv_urls = list()

    for link in page_soup.find_all('a'):
        page_urls.append(link.get('href'))

    for link in page_urls:
        if link.split('.')[1] == 'csv':
            csv_url = 'http://www.football-data.co.uk/' + link

            if csv_url not in csv_urls:  # prevent duplicates
                csv_urls.append(csv_url)

    return csv_urls


def main():
    base_dir = sys.argv[1]

    if not os.path.isdir(sys.argv[1]):
        os.mkdir(base_dir)

    download_pages(MAIN_COUNTRIES, 1, base_dir)
    download_pages(EXTRA_COUNTRIES, 0, base_dir)


if __name__ == '__main__':
    main()
