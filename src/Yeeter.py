from selenium import webdriver
import pandas as pd
import time
import json

class Yeeter:
    def __init__(self, config_path):
        self.config = self.read_config(config_path)
        self.tweets = []

    def scrape_user(self, user, num_tweets, until_point='', alt_date=None):
        user = user.lower()
        url = f"https://twitter.com/search?q=from%3A{user}{until_point}&src=typed_query&f=live"

        driver = webdriver.Chrome(self.config['selenium-driver'])
        driver.get(url) if not alt_date else driver.get(
            f"https://twitter.com/search?q=from%3A{user}{self.until(alt_date)}&src=typed_query&f=live"
        )

        time.sleep(0.3)

        no_load_top, no_load_bottom = False, False
        while len(self.tweets) <= num_tweets and not no_load_top:
            counter = 0
            while counter <= 2000 and not no_load_bottom:
                try:
                    driver.execute_script("""
                        window.scrollTo(0, document.body.scrollHeight);
                    """)
                    time.sleep(0.5)
                    tweet_chunk = driver.execute_script("""
                        chunk = []

                        let feed = Array.prototype.slice.call(document.querySelector("[aria-label='Timeline: Search timeline']").firstElementChild.children)
                        for(tweet of feed){
                            content = tweet.querySelector("[lang='en']")
                            date = tweet.querySelector('Time')
                            if(content){
                                chunk.push([date.dateTime, content.innerText])
                            }
                        }
                        return chunk
                    """)
                    self.tweets += [tweet for tweet in tweet_chunk if not tweet in self.tweets and self.is_clean(tweet[1])]
                    counter += len(tweet_chunk)
                    time.sleep(0.15)
                except:
                    print('Processing Ended: Broke Child Loop')
                    no_load_bottom = True
                    break
            print(len(self.tweets))
            try:
                driver.quit()
                time.sleep(1)
                new_date = self.tweets[-1][0].split('T')[0]
                if new_date == alt_date:
                    no_load_top = True
                    break
                else:
                    self.scrape_user(user, num_tweets, alt_date=new_date)
            except:
                print('Processing Ended: Broke Parent Loop')
                no_load_top = True
                break
        driver.quit()
        pass

    def to_df(self):
        return pd.DataFrame(self.tweets, columns=['Date', 'Tweet'])

    def to_csv(self, title, clear_tweets=False):
        df = self.to_df()
        df.to_csv(f'./{title}.csv', index=False, encoding='utf-8-sig')
        if clear_tweets:
            self.tweets = []

    @staticmethod
    def read_config(config_path):
        with open(config_path, 'r') as file:
            config = json.load(file)
        return config

    @staticmethod
    def until(until_point):
        if until_point:
            return '%05until%3A' + until_point
        else:
            return ''

    @staticmethod
    def is_clean(tweet):
        if '\n' in [letter for letter in tweet]:
            return False
        return True
