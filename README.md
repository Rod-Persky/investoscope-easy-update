# Investoscope Easy Update

Updates [Investoscope 3](http://www.investoscope.com/) end of day quotes from
different data sources than Yahoo or Google.

Right now it supports [Yahoo](http://www.yahoo.com/) as a data source and
it shouldn't bee too much work extending it to other local data sources which may
be updated faster after the local market closes than Yahoo and Google does.

It updates Investoscope by importing CSV in to Investoscope via Applescript.

Thanks to the founder of Investoscope Morten Fjord-Larsen who gave me a clue on how to express the Applescript and Thorbjørn Hermansen who made this in node.js.


## Supported markets

* Most - via yahoo.com

## Usage

### Preparation in Investoscope

When we update end of day quotes with this script we'll read quotes from
Investoscope's database and we try to update all stocks which have data in
the symbol field.

### First time install

```bash
# Clone
git clone https://github.com/Rod-Persky/investoscope-easy-update.git
cd investoscope-easy-update

# edit the script (investoscope_update.py) and edit so that
# INVESTOSCOPE_PATH = "~/.investoscope"
# points to Investoscope's data folder. The data folder may be
# changed in Investoscope's preferences, under the advanced tab.

```

#### Debug information
No debug information is output, for some instruments (bonds) the script
will output a type error because you may not be able to download its
historic data. This will happen every time the script runs, but it will
continue without any problems.

### To update Investoscope's quotes
```bash
python3 investoscope_update.py
```
