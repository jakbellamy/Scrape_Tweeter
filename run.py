from src.Yeeter import Yeeter



twitter = Yeeter('yeeter.json')
twitter.scrape_user('dril', 1500)
twitter.to_csv('dril_tweets')

