from selenium import webdriver
import pandas as pd 
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
import time
from datetime import date
from selenium.common.exceptions import NoSuchElementException

driver = webdriver.Firefox()
driver.get('https://www.indeed.co.uk/')
class_select = driver.find_element_by_link_text('Sign in')
class_select.click()
time.sleep(10)

email = '##'
password = '##'
id_box = driver.find_element_by_id('login-email-input')
pass_box = driver.find_element_by_id('login-password-input')
time.sleep(5)
id_box.send_keys(email)
pass_box.send_keys(password)
login_button = driver.find_element_by_id('login-submit-button')
login_button.click()

time.sleep(5)
what_job_box = driver.find_element_by_id('text-input-what')
where_job_box = driver.find_element_by_id('text-input-where')
role = 'analyst'
location = 'Birmingham'
what_job_box.send_keys(role)
where_job_box.send_keys(location)
search_button = driver.find_element_by_class_name('icl-Button')
search_button.click()

pageUrl = driver.current_url

df = pd.DataFrame(columns=["Title","Location","Company","Salary","Sponsored","Description", "QuickApply?","Links"])
jobs = []
for i in range(0,150,10):
    try:

        elems_list = []
        anotherUrl = pageUrl[:-3] + '&start='+str(i)
        driver.get(anotherUrl)

        driver.implicitly_wait(2)
        try:
            expopup = job.find_element_by_id('popover-x')
            expopup.click()   
        except:
            pass
        elems = driver.find_elements_by_xpath("//a[@href]")
        for elem in elems:
            elems_list.append(elem.get_attribute("href"))
        job_links = [i for i in elems_list if i[-4:]=='js=3']    

        pageJobNo = 0 
        for job in driver.find_elements_by_class_name('result'):
            try:
                driver.implicitly_wait(2)
                try:
                    expopup = driver.find_element_by_id('popover-x')
                    expopup.click()   
                except:
                    pass
                soup = BeautifulSoup(job.get_attribute('innerHTML'),'html.parser')
                try:
                    title = soup.find("a",class_="jobtitle").text.replace("\n","").strip()
                except:
                    title=None
                try:
                    location = soup.find(class_="location").text
                except:
                    location = 'None'

                try:
                    company = soup.find(class_="company").text.replace("\n","").strip()
                except:
                    company = 'None'

                try:
                    salary = soup.find(class_="salary").text.replace("\n","").strip()
                except:
                    salary = "None"

                try:
                    sponsored = soup.find(class_="sponsoredGray").text
                    sponsored = "Sponsored"
                except:
                    sponsored = "Organic"

                try:
                    anotherdriver = webdriver.Firefox()
                    anotherdriver.get(job_links[pageJobNo])
                    anotherdriver.implicitly_wait(2)
                    descr = anotherdriver.find_element_by_id('jobDescriptionText').text  
                    try:
                        anotherdriver.find_element_by_id('viewJobButtonLinkContainer')
                        quickapply = 'No'
                    except NoSuchElementException:
                        quickapply = 'Yes'
                except:
                    descr = "None"
                    quickapply = "None"
                anotherdriver.close()

                df = df.append({'Title':title,'Location':location,"Company":company,"Salary":salary,
                                "Sponsored":sponsored,"Description":descr, "QuickApply?":quickapply,
                                "Links":job_links[pageJobNo]},ignore_index=True)
                pageJobNo+=1
            except:
                pageJobNo+=1
    except:
        pass
        
csvname = role.replace(' ', '') + location + str(date.today()) + '.csv'
df.to_csv(csvname)
