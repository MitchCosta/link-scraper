from bs4 import BeautifulSoup
from selenium import webdriver
import time
import json


class MyScraper:

    def __init__(self, user, pw):
        self.username = user
        self.password = pw
        self.url_list = []
        self.driver = webdriver.Chrome("chromedriver")


    def login(self):
        # head to github login page
        self.driver.get("https://linkedin.com/login")
        self.driver.find_element_by_id("username").send_keys(self.username)
        self.driver.find_element_by_id("password").send_keys(self.password)
        # hit submit button
        self.driver.find_element_by_xpath('//*[@type="submit"]').click()

    def set_search(self, list_to_search):
        # list of search parameters : ["head of people", "head of people culture", "head of people operations"]
        # return a list of url's
        links_to_search = []
        for parameters in list_to_search:

            search = parameters.split()
            search = "%20".join(search)
            search += "%20"
            url = 'https://www.linkedin.com/search/results/people/?keywords='
            search_url = url + search
            links_to_search.append(search_url)

        return links_to_search

    def search_people(self, links_to_search, number_to_achieve):
        # a list of "ready to search" url's
        # int, number of search per item in the previous list
        # url = 'https://www.linkedin.com/search/results/people/?keywords=head%20of%20people%20brisbane&sid=q8P'
        # Output -> a list people links

        people_links = []

        for url in links_to_search:

            number_of_links = 0
            print(f"Search url -> {url}")
            self.driver.get(url)

            while number_of_links < number_to_achieve:

                req = self.driver.page_source

                soup = BeautifulSoup(req, "html.parser")

                anchor_tags = soup.find_all(name='a', class_='app-aware-link')
                for links in anchor_tags:
                    if len(links.get("href")) < 146 and number_of_links < number_to_achieve:
                        # the longer links are shared connections links
                        people_links.append(links.get("href"))
                        # In linkedIn we get roughly 2 links per person
                        number_of_links += 0.5

                # remove duplicates
                # remove duplicates of the total pages (after the next)
                print(f"before clean the duplicates -> {len(people_links)}")
                # first for loop detects triplicates and 4xs
                for _ in range(1, 3):
                    for link in people_links:
                        if people_links.count(link) >= 2:
                            people_links.remove(link)
                    print(len(people_links))

                print("sleep for 2 sec")
                time.sleep(2)
                self.driver.execute_script("window.scrollTo(0, 1000)")
                print("sleep for 2 sec")
                time.sleep(2)

                # number_of_links += len(people_links)
                # check if need to click NEXT (chevron)
                print(f" number_of_links {number_of_links}")
                print(f" number_to_achieve {number_to_achieve}")

                if number_of_links <= number_to_achieve:
                    self.driver.find_element_by_xpath('//*[@type="chevron-right-icon"]').click()
                    print("CLICKED  CLICKED  CLICKED  CLICKED")
                    print("sleep for 3 sec")
                    time.sleep(2)


        # remove duplicates of the total pages (after the next)
        print(f"before clean the duplicates -> {len(people_links)}")
        for _ in range(1, 3):
            for link in people_links:
                if people_links.count(link) >= 2:
                    people_links.remove(link)
            print(len(people_links))

        for people in people_links:
            print(people)
        # print(len(people_links))
        return people_links

    def search_profile(self, url):
        # NOT USED   NOT USED   NOT USED   NOT USED
        # input -> link to profile
        # output -> list with result

        # url = 'https://www.linkedin.com/in/emmadwyer?miniProfileUrn=urn%3Ali%3Afs_miniProfile%3AACoAAAEy3yEBpLbsxI5oKhT4UFKJ0et4gdSzk5Q'
        self.driver.get(url)
        req = self.driver.page_source

        soup = BeautifulSoup(req, "html.parser")

        # name = soup.find_all(name='h1', class_='top-card-layout__title')
        # company = soup.find_all(name='div', class_='inline-show-more-text')
        # about = soup.find_all(name='div', class_='inline-show-more-text')

        another = self.driver.find_element_by_xpath('//*[@type="submit"]')
        name = self.driver.find_element_by_xpath('//*[@id="ember42"]/div[2]/div[2]/div[1]/div[1]/h1').text
        title = self.driver.find_element_by_xpath('//*[@id="ember42"]/div[2]/div[2]/div[1]/div[2]').text
        company = self.driver.find_element_by_xpath('//*[@id="ember42"]/div[2]/div[2]/ul/li[1]/a/h2/div').text
        location = self.driver.find_element_by_xpath('//*[@id="ember42"]/div[2]/div[2]/div[2]/span[1]').text
        # about = self.driver.find_element_by_xpath('//*[@id="ember156"]/div').text
        about = "Cannot get it"
        # about = soup.find(name='div', class_='inline-show-more-text')

        print(name)
        print(title)
        print(company)
        print(location)
        print(about)

        return [name, title, company, location, about]

    def search_profile_fyang(self, url):

        self.driver.get(url)
        req = self.driver.page_source
        soup = BeautifulSoup(req, "html.parser")

        profile_tag = self.find_profile_data(soup)
        # print(profile_tag)
        if profile_tag is None:
            return None
        else:
            profile_data = {}
            json_data = json.loads(profile_tag.getText())
            # print("-------------------------------------------")
            # print(json_data)
            for key in json_data["included"]:
                # print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
                # print(key)
                if "firstName" in key:
                    name = f"{key['firstName']} {key['lastName']}"
                    profile_data["name"] = name
                    headline_parts = key["headline"].split("at")
                    profile_data["title"] = headline_parts[0].strip()
                    if len(headline_parts) > 1:
                        profile_data["company"] = headline_parts[1].strip()
                    if "summary" in key:
                        profile_data["about"] = key["summary"]
                elif "countryUrn" in key:
                    profile_data["location"] = key["defaultLocalizedName"]
                elif "companyName" in key and "dateRange" in key:
                    date_range = key["dateRange"]
                    if date_range is None or "end" not in date_range:
                        profile_data["company"] = key["companyName"]
                print(profile_data)
            if "name" in profile_data:
                return [profile_data['name'], profile_data['title'], profile_data['company'], profile_data['location'], profile_data['about'], ]
            else:
                return None

    def find_profile_data(self, soup):
        tags = soup.find_all("code")
        for tag in tags:
            if "multiLocaleSummary" in tag.getText():
                return tag
        return None
