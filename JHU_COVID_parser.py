#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from datetime import datetime
import pandas as pd
import argparse
import matplotlib.pyplot as plt
import seaborn as sns


def get_covid_data_filenames_and_dates(repo_path: str, start_date: str, end_date: str) -> tuple:
    path = os.path.join(repo_path, 'COVID-19/csse_covid_19_data/csse_covid_19_daily_reports')
    fn = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) if '.csv' in f]
    fn.sort()
    if end_date != 'latest':
        end_index = fn.index(end_date + '.csv') + 1
        fn = fn[:end_index]
    index = fn.index(start_date + '.csv')
    fn1 = fn[index - 1:]
    d1 = [z[0] for z in [x.split('.') for x in fn1]]
    d = [datetime.strptime(dt, '%m-%d-%Y') for dt in d1]
    f_p = [os.path.join(path, f) for f in fn1]
    return f_p, d


def generate_dataframes(filenames: list) -> list:
    return [pd.read_csv(df) for df in filenames]


def filter_covid_dataframes(dataframes: list, filter_covid: dict) -> list:
    filter_covid_list = list()
    for d in dataframes:
        if filter_covid.get('country') and filter_covid.get('state') and filter_covid.get('county'):
            try:
                filter_covid_list.append((d['Country_Region'] == filter_covid.get('country')) & (
                        d['Province_State'] == filter_covid.get('state')) & (d['Admin2'] == filter_covid.get('county')))
            except:
                filter_covid_list.append((d['Country/Region'] == filter_covid.get('country')) & (
                        d['Province/State'] == filter_covid.get('state')) & (d['Admin2'] == filter_covid.get('county')))
        elif filter_covid.get('country') and filter_covid.get('state'):
            try:
                filter_covid_list.append((d['Country_Region'] == filter_covid.get('country')) & (
                        d['Province_State'] == filter_covid.get('state')))
            except:
                filter_covid_list.append((d['Country/Region'] == filter_covid.get('country')) & (
                        d['Province/State'] == filter_covid.get('state')))
        elif filter_covid.get('country'):
            try:
                filter_covid_list.append((d['Country_Region'] == filter_covid.get('country')))
            except:
                filter_covid_list.append((d['Country/Region'] == filter_covid.get('country')))
    result_records = list()
    counter = 0
    for d in dataframes:
        try:
            result_records.append(d[filter_covid_list[counter]])
            counter += 1
        except Exception as e:
            print(e)
    return result_records


def get_data(column_name: str, dataframes: list) -> list:
    results_list = [c[column_name].sum(axis=0, skipna=True) for c in dataframes]
    delta_list = list()
    counter = 0
    for i in results_list:
        if counter == 0:
            delta_list.append(i - 0)
            counter += 1
        else:
            index = counter - 1
            delta_list.append(i - results_list[index])
            counter += 1
    return delta_list


def get_dates(dates: list) -> list:
    results = list()
    for date in dates:
        results.append(date.strftime('%m-%d'))
    return results


def generate_and_save_chart(x, y, *, y_limit: int = 0, y_label: str = '', column_name: str = '', location: dict, ):
    fig, ax = plt.subplots()
    if not y_limit:
        y_limit = max(y)
    ax.set_ylim(0, y_limit)
    ax.set_ylabel(y_label)
    fig.autofmt_xdate()
    ax.set_title(
        f"{location.get('county', '')} {location.get('state', '')} {location.get('country', '')} Per Day COVID-19 {column_name} ({x[0]} - {x[-1]})")
    palette = sns.color_palette("Blues")
    plt.annotate('Novel Coronavirus (COVID-19) Cases, provided by JHU CSSE, https://github.com/CSSEGISandData/COVID-19',
                 (0, 0), (-35, -40), fontsize=6,
                 xycoords='axes fraction', textcoords='offset points', va='top')
    ax = sns.barplot(x=x, y=y, palette=palette)
    save_filename = f"{location.get('country', '')}{location.get('state', '')}{location.get('county', '')}{column_name}_{x[0]}_{x[-1]}.png"
    fig.savefig(save_filename)
    print(f'{save_filename} saved!')


if __name__ == '__main__':
    """
    Examples:
    python JHU_COVID_parser.py
    python JHU_COVID_parser.py -sd=04-10-2020
    python JHU_COVID_parser.py -sd=06-01-2020 -f=Confirmed -c=US -s=Florida -co=Pasco -r=/Users/stmosher/PycharmProjects/
    python JHU_COVID_parser.py -sd=06-01-2020 -f=Deaths -c=US -s=Florida -co=Pasco -r=/Users/stmosher/PycharmProjects/
    python JHU_COVID_parser.py -sd=06-01-2020 -f=Deaths -c=US -s=Florida
    python JHU_COVID_parser.py -sd=06-01-2020 -f=Confirmed -c=US -s=Florida
    python JHU_COVID_parser.py -sd=06-01-2020 -ed=07-01-2020 -f=Deaths -c=US -s=Florida
    """
    parser = argparse.ArgumentParser(
        description='Build a custom COVID-19 graph based on your parameters.')
    parser.add_argument('--start_date', '-sd',
                        action='store',
                        default='03-22-2020',
                        help=('Start Date using format MM-DD-YYYY'))

    parser.add_argument('--end_date', '-ed',
                        action='store',
                        default='latest',
                        help=('End Date using format MM-DD-YYYY'))

    parser.add_argument('--filter_column', '-f',
                        action='store',
                        default='Confirmed',
                        help=('Options: Deaths or Confirmed'))

    parser.add_argument('--country', '-c',
                        action='store',
                        default='US',
                        help=('Limits graph to country specified. Example: US'))

    parser.add_argument('--state', '-s',
                        action='store',
                        default='',
                        help=('Limits graph to state specified. Example: Florida'))

    parser.add_argument('--county', '-co',
                        action='store',
                        default='',
                        help=('Limits graph to state specified. Example: Pasco'))

    parser.add_argument('--graph_title', '-g',
                        action='store',
                        default='',
                        help=('Use to give graph a custom name.'))

    parser.add_argument('--y_label', '-y',
                        action='store',
                        default='',
                        help=('Use a custom y label'))

    parser.add_argument('--y_limit', '-yl',
                        action='store',
                        default=0,
                        help=('Use to specify a custom y limit.'))
    parser.add_argument('--repo_path', '-r',
                        action='store',
                        default='/Users/stmosher/PycharmProjects/',
                        help=(
                            "Add path to the previous cloned https://github.com/CSSEGISandData/COVID-19. Example '/Users/stmosher/PycharmProjects/'"))

    args = parser.parse_args()

    location_filter_covid = dict(country=args.country, state=args.state, county=args.county)

    files, dates = get_covid_data_filenames_and_dates(repo_path=args.repo_path,
                                                      start_date=args.start_date,
                                                      end_date=args.end_date)
    df_covid_list = generate_dataframes(filenames=files)
    df_filtered_covid_list = filter_covid_dataframes(dataframes=df_covid_list, filter_covid=location_filter_covid)
    plot_data = get_data(column_name=args.filter_column, dataframes=df_filtered_covid_list)
    plot_dates = get_dates(dates)
    generate_and_save_chart(x=plot_dates[1:], y=plot_data[1:], y_limit=int(args.y_limit), y_label=args.y_label,
                            column_name=args.filter_column,
                            location=location_filter_covid)
