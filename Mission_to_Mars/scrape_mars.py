import requests
from bs4 import BeautifulSoup
from splinter import Browser
import pandas as pd
import time
import pymongo


# Create connection variable
conn = 'mongodb://localhost:27017'

# Pass connection to the pymongo instance.
client = pymongo.MongoClient(conn)

# Connect to a database. Will create one if not already available.
db = client.mars_db

# Drops collection if available to remove duplicates
db.planet.drop()




def scrape():
    # start browser
    executable_path = {'executable_path': 'chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=False)

    # NASA Mars News
    mars_url = 'https://mars.nasa.gov/news/?page=0'
    browser.visit(mars_url)

    time.sleep(5)

    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    articles = soup.find('ul', class_='item_list')
    news_title = articles.find('div', class_='content_title').text
    news_p = soup.find('div', class_='article_teaser_body').text

    # JPL Mars Space Images
    jpl_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(jpl_url)

    time.sleep(5)

    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    header = soup.find('div', class_='carousel_container')
    feature_pic = header.find('article')
    pic_background = feature_pic['style']
    pic_id = pic_background[53:61]
    featured_image_url = f'https://www.jpl.nasa.gov/spaceimages/images/largesize/{pic_id}_hires.jpg'

    # Mars Weather
    twitter_url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(twitter_url)

    time.sleep(5)

    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    tweets = soup.find('div', class_="css-1dbjc4n")
    mars_weather = tweets.find('div', lang='en').text

    # Mars Facts
    url_facts = 'https://space-facts.com/mars/'
    browser.visit(url_facts)

    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    facts_table = pd.read_html(url_facts)
    mars_facts_table = facts_table[0]
    mars_facts_table.columns = ["Parameter", "Value"]

    table_html = mars_facts_table.to_html()

    # Mars Hemispheres
    usgs_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(usgs_url)

    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    all_hemispheres = soup.find('div', class_='collapsible results')
    hemispheres = all_hemispheres.find_all('div', class_='item')

    beginning_url = 'https://astrogeology.usgs.gov'

    hemisphere_image_urls = []

    for result in hemispheres:
        hemisphere = result.find('div', class_="description")
        title = hemisphere.h3.text

        ending_url = hemisphere.a["href"]    
        browser.visit(beginning_url + ending_url)

        image_html = browser.html
        image_soup = BeautifulSoup(image_html, 'html.parser')

        image_link = image_soup.find('div', class_='downloads')
        image_url = image_link.find('li').a['href']

        hemisphere_dict = {}
        hemisphere_dict['title'] = title
        hemisphere_dict['img_url'] = image_url

        hemisphere_image_urls.append(hemisphere_dict)

    # Collect Data into one dictionary
    mars_dict = {
        "news_title": news_title,
        "news_p": news_p,
        "featured_image_url": featured_image_url,
        "mars_weather": mars_weather,
        "fact_table": table_html,
        "hemispheres_images": hemisphere_image_urls
    }

    # Creates a collection in the database and inserts two documents
    db.planet.insert_many([
        
        mars_dict
        ]
    )

    browser.quit()