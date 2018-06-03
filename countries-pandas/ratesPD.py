import requests
import json
import pandas as pd
import numpy as np
import datetime
import os
from configparser import ConfigParser


def createCountries():
    df_countries = pd.DataFrame(columns=['countryName',
                                         'callingCodes',
                                         'capital',
                                         'population',
                                         'currencies',
                                         'flag',
                                         'alpha3Code'])

    response_countries = requests.get('https://restcountries.eu/rest/v2/all')
    json_data_countries = json.loads(response_countries.text)

    i = 0
    for country in json_data_countries:
        df_countries.loc[i] = [country['name'],
                               country['callingCodes'],
                               country['capital'],
                               country['population'],
                               country['currencies'],
                               country['flag'],
                               country['alpha3Code']]
        i = i + 1

    # expand Currencies column: e.g. [{'code': 'AUD', 'name': 'Australian dollar', 'symbol': '$'}]  into 3 separate columns
    df_countries = pd.concat([df_countries, df_countries['currencies'].apply(lambda x: x[0]).apply(pd.Series)], axis=1,
                             join_axes=[df_countries.index])
    df_countries = df_countries.rename(columns={'name': 'currencyName'})
    df_countries = df_countries.rename(columns={'code': 'currencyCode'})
    df_countries = df_countries.drop('currencies', 1)

    # convert calling codes from list to str
    df_countries['callingCodes'] = df_countries['callingCodes'].apply(lambda x: x[0])

    return df_countries


def createRates(n, key):
    df_cur = pd.DataFrame(columns=['date', 'rates'])

    day = datetime.timedelta(days=1)
    today = datetime.datetime.now().date()
    date_in_the_past = today - datetime.timedelta(days=n)

    j = 0
    while date_in_the_past < today:
        response_currencies_date = requests.get('http://data.fixer.io/api/' +
                                                date_in_the_past.strftime('%Y-%m-%d') +
                                                '?access_key=' + key + '&format=1')
        json_data_currencies_date = json.loads(response_currencies_date.text)
        df_cur.loc[j] = np.array([json_data_currencies_date['date'], json_data_currencies_date['rates']])
        date_in_the_past = date_in_the_past + day
        j = j + 1

    # expand rates column <df_cur['rates'].apply(pd.Series)> in df_cur currencies table
    df_currencies = df_cur['date'].to_frame().join(df_cur['rates'].apply(pd.Series))

    return (df_currencies)


def convertToDict(target_countries):
    target_cur = []
    for c in target_countries:
        target_cur.append(df_countries[df_countries['alpha3Code'] == c]['currencyCode'].iloc[0])
    return {country: df_countries[df_countries['alpha3Code'] == country]['currencyCode'].iloc[0] for country in
            target_countries}


def computeMean(df_currencies, target):
    # compute mean for all currencies
    df_mean_rates_all = df_currencies.mean()

    # creating mean currencies result table for target countries
    df_mean_rates_target = pd.DataFrame(columns=['alpha3Code',
                                                 'meanCurrency'])
    i = 0
    for country, currency in target.items():
        # to exclude '(none)', None, rtc. OR given currency code doesn't exist in rates data
        if isinstance(currency, str) and len(currency) == 3 and currency in df_mean_rates_all:
            df_mean_rates_target.loc[i] = [country, df_mean_rates_all[currency]]
        else:
            df_mean_rates_target.loc[i] = [country, np.NAN]
        i = i + 1

    # merge countries table and mean rates table
    df_report = pd.merge(df_countries, df_mean_rates_target, how='inner', on=['alpha3Code'])
    pd.options.display.float_format = '{:.3f}'.format

    return df_report


def reportCSV(df_report):
    df_report['capital'].replace(",", "", regex=True, inplace=True)
    df_report.to_csv('out.csv', index=False, encoding='utf-8-sig', float_format='%.4f')


def reportHTML():
    try:
        os.mkdir('img')
    except:
        pass
    d = os.path.join(os.path.curdir, 'img')

    try:
        os.remove('mystyle.css')
    except OSError:
        pass

    with open('mystyle.css', 'w') as fs:
        fs.write("th {background-color: #f4d041; "
                   "font-family: arial, helvetica, "
                   "lucida-sans, sans-serif; "
                   "text-align: left; "
                   "padding: 15px; "
                   "height: 50px; "
                   "border: 2px solid white;}")
        fs.write("td {background-color: #f7f7f7; "
                   "font-family: arial, helvetica, lucida-sans, sans-serif; "
                   "text-align: left; "
                   "padding: 15px; "
                   "border: "
                   "2px solid white;}")
        fs.write("table {width: 100%; "
                   "border: none;}")
        fs.write("img {display: inline-block; "
                   "width: 70;}")

    try:
        os.remove('report.html')
    except OSError:
        pass

    with open('report.html', 'w') as f:
        f.write("<head>")
        f.write("<link rel='stylesheet' type='text/css' href='mystyle.css'>")
        f.write("<meta charset='UTF-8'>")
        f.write("</head>")

        f.write("<table border='0' class='dataframe'>")
        f.write("<link rel='stylesheet' type='text/css' href='mystyle.css'>")
        f.write("<meta charset='UTF-8'>")
        f.write("</head>")

        f.write("<table>")
        f.write("<tbody>")
        csvFile = open("out.csv", "r")
        flag = 0
        for line in csvFile:
            row = line.split(",")
            if flag == 0:
                f.write("<thead>")
                f.write("<tr>")
                f.write("<th>%s</td>" % row[0])
                f.write("<th>%s</td>" % row[1])
                f.write("<th>%s</td>" % row[2])
                f.write("<th>%s</td>" % row[3])
                f.write("<th>%s</td>" % row[4])
                f.write("<th>%s</td>" % row[5])
                f.write("<th>%s</td>" % row[6])
                f.write("<th>%s</td>" % row[7])
                f.write("<th>%s</td>" % row[8])
                f.write("<th>%s</td>" % row[9])
                f.write("</tr>")
                f.write("</thead>")
                flag = 1
            else:
                f.write("<tr>")
                f.write("<td>%s</td>" % row[0])
                f.write("<td>%s</td>" % row[1])
                f.write("<td>%s</td>" % row[2])
                f.write("<td>%s</td>" % row[3])
                r = requests.get(row[4])
                name = row[4].split('/')[-1]
                open(os.path.join(d, name), 'wb').write(r.content)
                f.write("<td><img src='%s'></td>" % os.path.join(d, name))
                f.write("<td>%s</td>" % row[5])
                f.write("<td>%s</td>" % row[6])
                f.write("<td>%s</td>" % row[7])
                f.write("<td>%s</td>" % row[8])
                f.write("<td>%s</td>" % row[9])
                f.write("</tr>")
        f.write("</tbody>")
        f.write("</table>")


if __name__ == "__main__":

    # Config variables
    cfg = ConfigParser()
    cfg.read('input.conf')

    # create all countries table
    df_countries = createCountries()

    # create rates table for n=30 days
    access_key = cfg.get('request', 'access_key')
    df_currencies = createRates(30, access_key)

    target_countries = cfg.get('request', 'countries').replace(' ', '').split(',')

    # create dictionary with target countries: corresponding currencies
    target = convertToDict(target_countries)

    # compute mean for target countries
    df_report = computeMean(df_currencies, target)

    # export report csv
    reportCSV(df_report)

    # export report html
    reportHTML()
