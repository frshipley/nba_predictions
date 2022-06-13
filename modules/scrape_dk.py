import datetime
import os
import dateutil
import dill as pickle
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

stat_dict = {'PTS': 'points',
             'REB': 'rebounds',
             'AST': 'assists',
             'FG3M': 'threes',
             'BLK': 'blocks',
             'STL': 'steals',
             'PR': 'pts-%2b-reb',
             'PA': 'pts-%2b-ast',
             'AR': 'ast-%2b-reb',
             'SB': 'steals-%2b-blocks',
             'PRA': 'pts,-reb-%26-ast'
             }


def urlBuilder(base, params):
    # selenium doesn't have a built-in URL builder for parameters, so stitch together base and parameters for full URL
    url = base
    url += "?"
    if params:
        for k, v in params.items():
            url += (k + "=" + v + "&")
    return url[:-1]


def parse(url):
    # scrape source code from rendered webpage
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    #response = webdriver.Chrome(os.path.join(os.path.pardir,"drivers","chromedriver.exe"),options=options)
    response = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    response.get(url)
    sourceCode = response.page_source
    return sourceCode


def getLines():
    base = "https://sportsbook.draftkings.com/leagues/basketball/88670846"  # NBA league ID = 88670846
    df_all = pd.DataFrame(columns=["PLAYER"])  # make an empty dataframe with a PLAYERS column for joining to later
    for category in stat_dict.keys():
        params = {'category': 'player-props',
                  'subcategory': stat_dict[category]  # this can be changed for whatever contest you like
                  }
        # make URL and parse HTML with beautiful soup
        url = urlBuilder(base, params)
        soup = BeautifulSoup(parse(url), features="lxml")
        # scrape the first table (should be the only table)
        x = soup.findAll("table")
        df = pd.DataFrame()

        latest_line_path = os.path.join(os.path.pardir, "logs","per_stat_lines", f"latest_line_{category}.pkl")

        for t in x:  # iterate over all of the tables (i.e. concatenate all upcoming games)
            temp_df = pd.read_html(t.prettify())[0]
            df = pd.concat([df, temp_df])
        try:  # try to load the line, over and under for the given stat
            # parse the line and odds from the dataframe
            df[[category + "_LINE", category + "_OVER"]] = df["OVER"].str.extract(r"[OU]([\W\w]*)([+|-]\d*)",
                                                                                  expand=True).apply(pd.to_numeric)
            df[category + "_UNDER"] = df["UNDER"].str.extract(r"[OU][\W\w]*([+|-]\d*)", expand=True).apply(
                pd.to_numeric)
            df = df[["PLAYER", category + "_LINE", category + "_OVER", category + "_UNDER"]]
            df.to_pickle(latest_line_path)  # cache these stats in case there is failure later
        except KeyError:  # if  stats cannot be loaded (because they haven't been posted), load cached ones
            print(f"Lines for {category} have not been posted yet for this contest. Please try again later.")
            print('In the mean time, we have loaded the last cached stats.')
            df = pd.read_pickle(latest_line_path)
        df_all = df_all.merge(df, how="outer", on="PLAYER")

    latest_line_path_all = os.path.join(os.path.pardir, "logs", f"latest_line_all.pkl")
    df_all.to_pickle(latest_line_path_all)  # cache these stats in case there is failure later
    return df_all


def getMatchupDetails():
    base = "https://sportsbook.draftkings.com/leagues/basketball/88670846"  # NBA league ID = 88670846
    params = {'category': 'player-props',
              'subcategory': 'points'  # this can be changed for whatever contest you like
              }
    # make URL and parse HTML with beautiful soup
    url = urlBuilder(base, params)
    soup = BeautifulSoup(parse(url), features="lxml")

    opponent_dict = dict()
    df_matchup = pd.DataFrame(columns=["GAME_DATE", "HOME", "AWAY"])

    matchups = soup.find_all("div", {"class": "sportsbook-event-accordion__title-wrapper"})
    game_dates = soup.find_all("span", {'class': 'sportsbook-event-accordion__date'})

    for datestr, match in zip(game_dates, matchups):
        logos = match.find_all("img")

        away_str = logos[0]['src']
        away_team = away_str.split('/')[-1].split('.png')[0]

        home_str = logos[1]['src']
        home_team = home_str.split('/')[-1].split('.png')[0]

        if datestr.text.split()[0] == 'Today':
            d = datetime.date.today()
        elif datestr.text.split()[0] == 'Tomorrow':
            d = datetime.date.today() + datetime.timedelta(days=1)
        else:
            d = dateutil.parser.parse(datestr.text).date()

        opponent_dict[home_team] = (away_team, d)
        opponent_dict[away_team] = (home_team, d)

    matchup_dict_path = os.path.join(os.path.pardir,"logs","upcoming_info.pkl")
    with open(matchup_dict_path, 'wb') as file:
        pickle.dump(opponent_dict, file)

    return opponent_dict


matchup_dict = getMatchupDetails()
lines = getLines()
