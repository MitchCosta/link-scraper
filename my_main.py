from my_scraper import MyScraper
import pandas
import time
import random

new_key = 0
new_list = []
people_data_dic = {
    "field_name": ["name", "title", "company", "location", "about"]
}

# insert your LinkedIn username and password in the constructor below
linkedin_scraper = MyScraper("your Username", 'Your password')

my_list = ["head of people", "head of people and culture", "head of people operations", "head of hr"]
number_per_search = 7

linkss = linkedin_scraper.set_search(my_list)
print(linkss)


linkedin_scraper.login()

# my_exp = linkedin_scraper.search_profile_fyang()
# print(my_exp)
#
# time.sleep(10)

total_links = linkedin_scraper.search_people(linkss, number_per_search)
print(f"TOTAL LINKS -> {len(total_links)}")

key = 1
for people in total_links:
    print(people)
    people_data_dic[key] = linkedin_scraper.search_profile_fyang(people)
    key += 1
    # sleep a bit, don't disturb the Gods
    time.sleep(3 + 3*random.random())

print(people_data_dic)

data_frame = pandas.DataFrame.from_dict(people_data_dic, orient='index')
data_frame.to_csv("people_file.csv")
