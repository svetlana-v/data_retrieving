import requests
import json
import MySQLdb
import datetime
import sys
from openpyxl import Workbook
from configparser import ConfigParser


def generateTableCountries(cursor):
    # create countries table:

    response_countries = requests.get('https://restcountries.eu/rest/v2/all')
    json_data_countries = json.loads(response_countries.text)

    cursor.execute("DROP TABLE IF EXISTS countries")
    cursor.execute(
        "create table IF NOT EXISTS countries (countryName varchar(100),callingCodes varchar(10),capital varchar("
        "100),population INT,currenciesCode varchar(10),currenciesName varchar(100),currenciesSymbol varchar(10), "
        "alpha3Code varchar(3), PRIMARY KEY (alpha3Code));")

    for country in json_data_countries:
        cursor.execute(
            "INSERT INTO countries (countryName,callingCodes,capital,population,currenciesCode,currenciesName,"
            "currenciesSymbol,alpha3Code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s);",
            (
                country['name'],
                country['callingCodes'][0],
                country['capital'],
                country['population'],
                country['currencies'][0]['code'],
                country['currencies'][0]['name'],
                country['currencies'][0]['symbol'],
                country['alpha3Code']))

    db.commit()
    print('Countries table is built.')

def generateTableRates(cursor, access_key, n):
    # create rates table for n days:

    cursor.execute("DROP TABLE IF EXISTS rates")
    cursor.execute("DROP TABLE IF EXISTS meanRates")

    day = datetime.timedelta(days=1)
    today = datetime.datetime.now().date()
    date_in_the_past = today - datetime.timedelta(days=n)

    cursor.execute("CREATE TABLE rates (datesInfo varchar(10),currenciesCode varchar(10),curRate FLOAT)")

    while date_in_the_past < today:
        response_currencies_date = requests.get('http://data.fixer.io/api/' + date_in_the_past.strftime(
            '%Y-%m-%d') + '?access_key=' + access_key + '&format=1')
        json_data_currencies_date = json.loads(response_currencies_date.text)

        # fill in the table
        for (code, value) in json_data_currencies_date['rates'].items():
            code = '\'{0}\''.format(code)
            cursor.execute(
                "INSERT INTO rates (datesInfo,currenciesCode,curRate) VALUES(%s,%s,%s);" % ('\'{0}\''.format(date_in_the_past), code, value))
        date_in_the_past = date_in_the_past + day

    db.commit()

    print('Rates table is built.')


def createReport(target_countries):

    wb = Workbook()

    cursor.execute("SELECT * from countries INNER JOIN (SELECT currenciesCode, AVG(curRate) AS meanRate FROM rates "
                   "GROUP BY currenciesCode) AS meanRates WHERE alpha3Code in ('%s') AND countries.currenciesCode = "
                   "meanRates.currenciesCode;" % "','".join(target_countries))
    results = cursor.fetchall()
    ws = wb["Sheet"]
    ws.title = "CountriesOverview"
    columns = [desc[0] for desc in cursor.description]
    ws.append(columns)

    for row in results:
        ws.append(row)

    workbook_name = "countriesWorkbook"
    wb.save(workbook_name + ".xlsx")
    print(workbook_name + '.xlsx report is created.')



if __name__ == "__main__":

    # Config variables
    cfg = ConfigParser()
    cfg.read('input.conf')

    # mysql credentials
    try:
        my_host = cfg.get('server', 'host')
        my_user = cfg.get('server', 'user')
        my_passwd = cfg.get('server', 'password')
    except:
        print('Make sure input.conf file has host, user and password variables specified...')
        sys.exit()

    db = MySQLdb.connect(host=my_host, user=my_user, passwd=my_passwd, charset='utf8')
    cursor = db.cursor()
    try:
        cursor.execute("USE rates")
    except:
        cursor.execute("CREATE DATABASE rates")

    cursor.execute("SET sql_notes = 0;")

    # access key for fixer.io rates data
    access_key = cfg.get('request', 'access_key')
    # number of days
    n = 30

    # generate mysql tables
    generateTableCountries(cursor)
    generateTableRates(cursor, access_key, n)

    # create excel report for target countries
    target_countries = cfg.get('request', 'countries').replace(' ', '').split(',')
    createReport(target_countries)

    cursor.execute("SET sql_notes = 1;")
    db.commit()
    db.close()
