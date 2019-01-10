# Mission to Mars

#Import dependencies

from splinter import Browser
from bs4 import BeautifulSoup
import requests
import pymongo
import tweepy
import json
import pandas as pd
from config import consumer_key, consumer_secret, access_token, access_token_secret
import time 

def init_browser():
    executable_path = {"executable_path": "/Users/stefa/chromedriver.exe"}
    return Browser("chrome", **executable_path, headless=False)

def scrape():
    
    #Create the dictionary that will store all of the Mars information we scrape
    mars_data = {}
    
    #scrape Nasa data
    headline, teaser, date = scrape_mars_headline()

    mars_data["nasa_headline"] = headline
    mars_data["nasa_teaser"] = teaser
    mars_data["nasa_date"] = date
    
    #scape JPL for featured image
    featured_image = scrape_JPL_image()
    mars_data["featured_image"] = featured_image
    
    #scrape Twitter for the latest Mars weather tweet
    mars_weather = mars_weather_tweet()
    mars_data["weather"] = mars_weather
   
    #scrape Mars Facts website to store basic facts on the planet
    facts_html_table = mars_facts()
    mars_data["facts_table"] = facts_html_table
    
    #scrape USGS to get images for each of Mars' hemispheres
    hemisphere_images = mars_hemispheres()
    mars_data["hemi_img"] = hemisphere_images
      
    return mars_data


def scrape_mars_headline():

    #This function scrapes the Nasa website for the latest news headline

    browser = init_browser()
      
    # visit https://mars.nasa.gov/news/
    mars_news = "https://mars.nasa.gov/news/"
    browser.visit(mars_news)
    
    #store the html in a variable called html    
    html = browser.html

    # create a soup object from the html.  This will parse the html we pulled from Nasa website.
    soup = BeautifulSoup(html, "html.parser")
   
    #Get the latest article posted on the site.  The list_text class has the headline,
    # date, and a blurb about the article - "a teaser"
    
    mars_article = soup.find('div', class_='list_text')

    #Now that we have the article, we can get the headline, blurb, and date
    mars_headline = mars_article.find('div', class_='content_title').text
    mars_teaser = mars_article.find('div', class_='article_teaser_body').text
    mars_news_date = mars_article.find('div', class_='list_date').text
    
    return mars_headline, mars_teaser, mars_news_date       

def scrape_JPL_image():
    
    #This function scrapes the JPL website for an image of Mars

    browser = init_browser()

    # visit https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars
    mars_jpl = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    
    browser.visit(mars_jpl)

    #store the html in a variable called html    
    html = browser.html

    #click on the button that says "FULL IMAGE"
    browser.click_link_by_partial_text('FULL IMAGE')

    time.sleep(2)

    #now click on the link that says "more info"
    browser.click_link_by_partial_text('more info')

    time.sleep(2)

    #we're on a new page so we need to scrape the html again
    new_html = browser.html

    #make a beautifulsoup object for the new page
    soup = BeautifulSoup(new_html, "html.parser")

    image_detail = soup.find('img', class_='main_image')

    full_res_jpeg = image_detail.get('src')

    #now append the jpl nasa front end link
    jpl = "https://www.jpl.nasa.gov"

    featured_image_url = jpl + full_res_jpeg

    print(f"JPL Featured Image: {featured_image_url}")
    
    return featured_image_url

def mars_weather_tweet():
        
    #get mars weather's latest tweet from the website

    browser = init_browser()

    weather_url = "https://twitter.com/marswxreport?lang=en"
    browser.visit(weather_url)

    html_weather = browser.html

    soup = BeautifulSoup(html_weather, "html.parser")

    mars_weather = soup.find("p", class_="TweetTextSize TweetTextSize--normal js-tweet-text tweet-text").text

    print(f"Latest Weather Tweet: {mars_weather}")
    
    return mars_weather

def mars_facts():

    #scrape the space-facts website to get basic data on the planet Mars

    #store the URL for the space facts website
    facts_url = "https://space-facts.com/mars/"

    #Use pandas to scrape the page for table data
    tables = pd.read_html(facts_url)
    tables

    facts_df = tables[0]
    facts_df.columns = ['Fact Type', 'Fact Data']
    facts_df
    
    #Convert the dataframe to an HTML table string

    facts_html_table = facts_df.to_html(header=False, index=False)


    #strip the \n characters
    facts_html_table = facts_html_table.replace('\n', '')
    
    print(facts_html_table)
    
    return facts_html_table

def mars_hemispheres():

    #scrape the entire 'collapsible results' class so that we can loop through each item

    #set the browser variable
    browser = init_browser()

    # visit https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars
    mars_usgs_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(mars_usgs_url)

    #store the html in a variable called usgs_html    
    usgs_html = browser.html

    # create a soup object from the html.  This will parse the html we pulled from USGS website.
    usgs_soup = BeautifulSoup(usgs_html, "html.parser")

    #Get the URL for the featured image-full size

    product_box = usgs_soup.find('div', class_='collapsible results')
    
    #create lists to hold the partial and full links to each hemisphere's page
    hemi_links = []
    hemi_urls = []

    for item in product_box.find_all('div', class_='item'):
        hemi_links.append(item.find('a').get('href'))

    #beginning of url to append
    link_beg = "https://astrogeology.usgs.gov"

    #create a new list to store the entire url string
    for link in hemi_links:
        link = link_beg + link
        hemi_urls.append(link)
 
    #visit each hemisphere's links using Splinter and get the images
    #Create an empty list to store the dictionaries for all hemispheres
    hemisphere_image_urls = []

    #Create an empty list to store the title and image link for each hemisphere
    hemi_dict = {}

    for url in hemi_urls:
        browser.visit(url)
        hemi_html = browser.html

        # create a soup object from the html. 
        hemi_soup = BeautifulSoup(hemi_html, "html.parser")

        #store the title
        title = hemi_soup.find('h2', class_='title').text
        title = title.replace(' Enhanced', '')
        
        print(f"Hemisphere: {title}")

        #go to the downloads section to get the list of images and pick the full image
        hemi_download = hemi_soup.find('div', class_='downloads')
        hemi_list = hemi_download.find('li')
        hemi_image = hemi_list.a['href']
        
        print(f"Image: {hemi_image}")

        hemi_dict = {'title' : title, 'image' : hemi_image}
    
        hemisphere_image_urls.append(hemi_dict)

    return hemisphere_image_urls






  
