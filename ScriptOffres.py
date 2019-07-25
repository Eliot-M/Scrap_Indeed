
# coding: utf-8

# # Récupération des offres depuis sites

# In[ ]:


# --- Import packages --- #
import pandas as pd

from datetime import date
import time
import random
import re

from selenium import webdriver #used to create session
from selenium.webdriver.chrome.options import Options # used for inconito mode
from selenium.webdriver.common.keys import Keys # used to simulate keyboard keys

import warnings
warnings.filterwarnings('ignore')
#


# In[ ]:


# --- Data scraper function --- #
def getJobData():
    '''
    Function used to get information from xpath. Collected data: job title, url of detailed offer, city, date, description preview
    
    input:
        None
        
    output: 
        new_df (df): pandas dataframe containing collected data (empty if any issue occurs during the scrap)
    
    '''
    
    # Get job titles and links
    titles_element = browser.find_elements_by_xpath("//a[@class='jobtitle turnstileLink ']")
    titles = [x.text for x in titles_element]
    links = [x.get_attribute("href") for x in titles_element]

    # Get company name
    company_element = browser.find_elements_by_xpath("//span[@class='company']")
    company = [x.text for x in company_element]
    
    # Get city location
    city_element = browser.find_elements_by_xpath("//div[@class='location'] | //span[@class='location']")
    city = [x.text for x in city_element]

    # Get date of post
    date_element = browser.find_elements_by_xpath("//div[@class='result-link-bar']")
    date = [x.text for x in date_element]
    date = [re.sub(r' - sauvegarder.*$', r'', w) for w in date]
    
    # Get description
    desc_element = browser.find_elements_by_xpath("//div[@class='summary']")
    desc = [x.text for x in desc_element]
    
        # If all field are complete (at least same length), store it
    if (len(titles) == len(company)) and (len(titles) == len(city)) and (len(titles) == len(date)) and (len(titles) == len(desc)):
        new_d = {'Job':titles, 'Company':company, 'Link':links, 'City':city, 'Posted':date, 'Description':desc}
        new_df = pd.DataFrame(new_d)
        print(str(browser.current_url) + " : Done")
    else:
        # Else return empty df, which have no impact and allow a unique format for return
        new_df = pd.DataFrame({'Job':[], 'Company':[], 'Link':[], 'City':[], 'Posted':[], 'Description':[]})
        print('Error in this url : ')
        print(browser.current_url)
        print('For information - posted : ' + str(len(date)) + ', titles : ' + str(len(titles)) + ', cities : ' + str(len(city)) + ', companies : ' + str(len(company)) + ', descriptions : ' + str(len(desc)) + '.')
    
    return new_df
#


# In[ ]:


# --- Crawler function --- #

def ScrapPages(job, city, pages_to_scrap = 1, driver_path ="/Users/eliotmoll/Documents/Data_Aticles_Pro/chromedriver"):
    '''
    Function to scrap pages for specific research (Job and city) using selenium.
    
    input:
        job (str): Job name.
        city (str): City for the job.
        pages_to_scrap (int): number of pages to scrap (at least 1). 1 will return the first page of result for the search.
        driver_path (str): path to executable driver (chrome in this case).
        
    output:
        df (df): pandas dataframe containing collected data and added infos like the date of the scraping (empty if any issue occurs during the scrap)
    '''
    
    # Set inconito session and define path to webdriver exe.
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")

    browser = webdriver.Chrome(executable_path = driver_path, chrome_options=chrome_options)

    # Define entry page
    browser.get("https://www.indeed.fr/")
    # Leave a little breaks for loading (1 to 2s)
    time.sleep(round(random.random() + 1))

    # Use input field to do the research
    inputElement = browser.find_element_by_id("text-input-what")
    inputElement.send_keys(job)

    inputElement2 = browser.find_element_by_id("text-input-where")
    
    # Remove all potential pre-write elements. 15 characters should be sufficient. Other selenium method seems to not work on mac+chrome
    for x in range(15):
        inputElement2.send_keys(Keys.BACK_SPACE)
    inputElement2.send_keys(city)

    time.sleep(round(random.random() + 1))

    # click on the search button
    browser.find_element_by_css_selector('.icl-Button.icl-Button--primary.icl-Button--md.icl-WhatWhere-button').click()

    # Let the fun begin
    df = pd.DataFrame({'Job':[], 'Company':[], 'Link':[], 'City':[], 'Posted':[], 'Description':[]})

    # Reach all pages
    for i in range(pages_to_scrap):
        time.sleep(round(random.random() * 2 +1, 1))
        # Get data, using the previously define function
        df = df.append(getJobData())
        # Find other pages links
        pages_n = browser.find_elements_by_xpath("//div[@class='pagination']/a")
        pages = [x.get_attribute("href") for x in pages_n]
        # If it's not the last page to scrap, load the next one.
        if i < pages_to_scrap:
            browser.get(pages[-1]) # Last element correspond to "Suivant/Next".


    browser.close()

    # Add information for reading
    df['isRead'] = 'no' # did you read this offer ? 
    df['New'] = 'yes' # is that a new offer (obtain from the last scrap) ?
    df['More'] = 'no' # do you want more information (get detailled description) ?
    df['MoreDone'] = 'no' # is the detailled scrap already done ?
    df['FullDescription'] = '-'
    # Add the date of the scrap session. Could also be used to determined the publish date of the offer
    today = date.today()
    scr_date = today.strftime("%d/%m/%Y")
    df['Date'] = scr_date

    print("Overall Done")
    print("------------")
    print(df.shape)
    
    return(df)

df = ScrapPages(job='Data Scientist', city='Paris', pages_to_scrap=2)
#


# In[ ]:


# --- Cleaning function to improve indeed results --- #
def cleaningOffers(input_df):
    '''
    Cleaning function to remove undesired offers.
    
    input:
        input_df (df): dataframe with offers. Need to have 'Job', 'Company', 'Description', 'City'
        
    output:
        input_df (df): dataframe with offers. Same format as input, just filtered.
    '''
    
    print(input_df.shape)
    # Convert fields to lowercase for search function
    input_df['Job'] = input_df['Job'].str.lower()
    input_df['Company'] = input_df['Company'].str.lower()
    input_df['Description'] = input_df['Description'].str.lower()
    input_df['City'] = input_df['City'].str.lower()
    
    
    # Keep only data science related jobs
    input_df = input_df[input_df['Job'].str.contains("scientist|science|research")]
    
    # Remove non full-time jobs
    input_df = input_df[~input_df['Job'].str.contains("alternan|stage|intern")]
    
    # Remove undesired seniority or function (consulting)
    input_df = input_df[~input_df['Job'].str.contains("lead|chief|chef|manager|senior|consult")]
    
    input_df = input_df[~input_df['Company'].str.contains("consult|conseil")]
    input_df = input_df[~input_df['Description'].str.contains("consult|conseil")]
        # Remove specific companies (like consulting firms).
    input_df = input_df[~input_df['Company'].str.contains("capgemini|novencia|kpmg|ey|mazars|accenture|sopra|avisia|ingeniance")]
    
    # Remove specific cities (far from home with public transportation)
    input_df = input_df[~input_df['City'].str.contains("villetaneuse")]
    
    # Remove commas to be sure to not have any issue with csv output    
    input_df.Job = input_df.Job.apply(lambda x: x.replace(',',' '))
    input_df.Description = input_df.Description.apply(lambda x: x.replace(',',' '))
    
    print(input_df.shape)
    
    return(input_df)

df = cleaningOffers(df)
#


# In[ ]:


# --- Add new offer to old ones --- #
# Load stored data
dfs = pd.read_csv('/Users/eliotmoll/Documents/Data_Aticles_Pro/Jobs/Scraps/job_found.csv')

# Change details, all loaded data are not anymore the most recent ones.
dfs['New'] = 'no'

# Add new offers
dfs = dfs.append(df)

# Remove overlapping jobs (based on Job, Company, City and Description). Keep the first one (which is the "old" one).
dfs = dfs.drop_duplicates(subset=['Job', 'Company', 'City', 'Description'], keep='first')

# Store back data
dfs.to_csv("/Users/eliotmoll/Documents/Data_Aticles_Pro/Jobs/Scraps/job_found.csv", index=False)
#


# In[ ]:


# Check new data
dfs = pd.read_csv('/Users/eliotmoll/Documents/Data_Aticles_Pro/Jobs/Scraps/job_found.csv')

dfs[dfs.New == 'yes']
#


# In[ ]:


# Manually define interesting offers

dfs.set_value(1, 'More', 'yes') # row index, column name, new value
#


# In[ ]:


# --- New selenium scraper for intersting offers --- #
def ScrapDetailPages(df, driver_path ="/Users/eliotmoll/Documents/Data_Aticles_Pro/chromedriver"):  
    '''
    Function to add full description information. 
    
    input:
        df (df): dataframe with offers. Need to have 'More', 'Link' and 'MoreDone'.
        driver_path (str): path to executable driver (chrome in this case).
    
    output:
        df (df): dataframe with offers and detailled description.
    '''
    
    # Set inconito session and define path to webdriver exe.
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")

    browser = webdriver.Chrome(executable_path="/Users/eliotmoll/Documents/Data_Aticles_Pro/chromedriver", chrome_options=chrome_options)
    
    # Get informations for specific offers
    for x in df[(df.More == 'yes') & (df.MoreDone == 'no')].Link:

        # Get url
        browser.get(str(x))
        
        time.sleep(round(random.random() + 1))

        # Get full description 
        details_element = browser.find_elements_by_xpath("//div[@class='jobsearch-jobDescriptionText']")
        details = [x.text for x in details_element]
            # Remove commas to be sure to not have any issue with csv output  
        details_clean = details[0].replace(",", " ")
        
        # Find indices to replace empty value with scraping results
        #indices = df.index[df['Links'] == x].tolist()
        #for i in indices:
            #df.set_value(i, 'FullDescription', details_clean)
        
        # Find indices to replace empty value with scraping results
        df[df.Link == x].FullDescription = details_clean
        df[df.Link == x].MoreDone = 'yes' #une fois OK
    
    browser.close()
    
    return(df)
#

