# Investoscope Easy Update

Primarily Investoscope Easy Update supports [Yahoo](http://www.yahoo.com/) as a data source and
it shouldn't be too much work extending it to other data sources that include more complex instruments.

## Supported markets

* Most - via yahoo.com

## Installation

1) Install python 3
2) Install python requests module `pip3 install requests`
3) Download this repository as a zip file
4) Extract Investoscope Updater.app to a convienient place
5) control click and open app and authorise the app

## Usage

1) Open Investoscope Updater! That's it

## Common Issues

The output will show any issue that has occrred giving a few seconds before
disappearing. You may wish to read the output to diagnose what happened, otherwise
simply open a git issue.

You will need python 3 installed, you should do this using either homebrew or
the official python installer. 

I will do not know how to code sign this app, you will have to enable the use of
apps from 'unknown' developers. The first time you open the app you will need to
control + click and select open from the menu.

The method is totally against all TOSs for these services, however the method
emulates you manually browsing to these sites -- we also are extremely concientious
about the data requests and download minimal data. These providers are within their
best interests to impliment anti-botting measures therefore I must stress that
*THERE IS NO WAY I CAN GUARENTEE THAT THE DATA IS ACCURATE*.

## Data Accuracy

1) Yahoo data for LSE is mixed in GBP and GBp. So this means that any reports done in Investoscope including those instruments are out by a factor of 100 for those instruments! This appears to be a known issue, with comments from November indicating Yahoo would look into it.

