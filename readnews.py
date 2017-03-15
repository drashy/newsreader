#!/usr/bin/python
# -*- coding: utf-8 -*-
########
# Listen to the local news on ChronicleLive
# Copyright 2016 Paul Ashton
#
# Uses gtts library from https://github.com/pndurette/gTTS
########

import re
import time
try:
  import requests
  from gtts import gTTS
  from pygame import mixer
except:
  print("Can't continue. The following packages are required: requests, gtts, pygame.")
  exit()

class readnews(object):
  def __init__(self):
    self.NEWSURL = "http://www.chroniclelive.co.uk/news/north-east-news/"
    self.NUMARTICLES = 3


  def DoFixes(self, text):
    #Substitutions (seems Chronicle can't decide on a standard)
    reps = ((r'&#xa;', ''), (r'&nbsp;', ''), (r'&#039;', '\''),
            (r'&#x27;', '\''), (r'&#x25;', '%'), (r'&#x3f;', '?'),
            (r'&#x28;', '('), (r'&#x29;', ')'), (r'&amp;', '&'),
            (r'L-R', 'Left-to-Right,'), (r'&quot;', '\''),
            (r'(?:\xa3|&pound;)(\d{1,3}[,m\d{3}]+)', r'\1 (POUNDS)'), #Handle pounds
            (r'[\'\"](.*?)[\'\"](?![s|r])', r'(QUOTE) \1 (UNQUOTE)') #Handle quotes
            )
    for rep in reps:
      text = re.sub(rep[0], rep[1], text)

    return text.strip() #Strip whitespace


  def getArticles(self, numarticles=10):
    """
    Get articles from webpage using only regex as XML libraries are bloaty and slow :)
    """
    print("Retrieving news...")
    articles = []
    try:
      html = requests.get(self.NEWSURL).text
      html = re.search(r'(?s)<section data-group="topStories">(.+?)</section>', html).group() # We are only interested in the top-stories section

      for article in re.findall(r'(?s)(<div class="teaser">.+?</div></div></div>)', html):
        headline = re.search(r'(?s)<strong><a href.+?>(.+?)</a></strong>', article).group(1)
        strapline = re.search(r'(?s)<div class="description"><a href.+?>(.+?)</a></div>', article).group(1)
        articles.append((headline, strapline))

        if len(articles) >= self.NUMARTICLES:
          break
    except:
      pass

    if not articles:
      exit("Error: Could not find any news - it is possible that the site is down")

    return articles


  def buildTopStories(self, articlelist):
    topstories = "Top {0} news articles from Chronicle Live:\n".format(len(articlelist))

    for n, article in enumerate(articlelist):
      headline = self.DoFixes(article[0])
      strapline = self.DoFixes(article[1])

      topstories += u"Article {0}:\n{1}\n{2}\n\n\n".format(n+1, headline, strapline)

    return topstories


  def textToMP3(self, text, filename="temp.mp3"):
    print("Converting to MP3..")
    tts = gTTS(text=text, lang='en')
    tts.save(filename)


  def playAndWait(self, filename="temp.mp3"):
    print("Playing..  (ctrl+c to stop)")
    mixer.init()
    mixer.music.load(filename)
    mixer.music.play()
    try:
      while(mixer.music.get_busy()):
        time.sleep(1)
    except KeyboardInterrupt:
      print("Stopped by user.")
    return True


  def readNews(self):
    articles = self.getArticles(self.NUMARTICLES)
    news = self.buildTopStories(articles)
    print(news)
    self.textToMP3(news)
    self.playAndWait()
    print("All done!")
    return False


if __name__ == '__main__':
  r = readnews()
  r.readNews()



