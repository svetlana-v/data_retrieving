Description
==================================================================

To launch the code:
    install required packages {'requests',
                               'mysql-connector',
                               'mysqlclient',
                               'openpyxl'},
    make sure mysql.server is started,
    enter required mysql parameters in input.conf {'host',
                                                   'user',
                                                   'password'},
    launch: >> python ratesSQL.py

File ratesSQL.py creates mysql table for all countries and
mysql table for the corresponding exchange rates for the past
n=30 days.

It is possible to set target countries in target_countries list
variable in input.conf by specifying corresponding alpha3Code.

The report is generated in .xlsx format for target countries.

To request exchange rates fixer.io web service is used.
This implies using of an access key that can be requested
via fixer.io website (an example of the key is specified
in input.conf).
