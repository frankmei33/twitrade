## Requirements:
Python 3

pyquery (pip install pyquery)


## Instruction
To use the Twitter scraping program, run the following command in conda environment:

```
python Exporter.py --querysearch "$TSLA" --since 2015-12-01 --until 2016-01-01
```

This command will save tweets with keyword "TSLA" from 2015-12-01 to 2016-01-01 to csv files each containing one day's tweets


## Update
04/11/17: fixed the language problem, use 'l=en' instead of 'lang=en'

Note: username is lost due to new json field name.

(Modified from: https://github.com/Jefferson-Henrique/GetOldTweets-python)
