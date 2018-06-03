Description
==================================================================

To launch the code install required packages
{'requests', 'pandas', 'numpy'} and launch:
>> python ratesPD.py

File ratesPD.py collects general info about all countries
together with the corresponding exchange rates for the past month
and computes mean values for it.

The code generates the following files:
	out.csv
	report.html
	/img
	mystyle.css

It is possible to set target countries in input.conf file
by specifying corresponding alpha3Code.

The reports are generated in .csv and .html (together with styles)
formats for target countries.

To request exchange rates fixer.io web service is used.
This implies using of an access key that can be requested
via fixer.io website (an example of the key is specified
in input.conf).
