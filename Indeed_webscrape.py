##
import requests
import bs4
from bs4 import BeautifulSoup
import argparse
import pandas as pd
import time

ap = argparse.ArgumentParser()
ap.add_argument('-URL', '--link', required=False,
                help='a string or a list of strings that specify the links of the job posting')
ap.add_argument('-no', '--page', required=False,
                help='The number of pages to scrape')
ap.add_argument('-fi', '--file', required=False,
                help='File to save info to')
args = vars(ap.parse_args())
## Import url
URL = 'https://www.indeed.com/jobs?q=Data+Scientist&l=Texas&explvl=entry_level'


def getJobInfo(divs):
    """Get job titles, locations, summary links, and companies' names from indeed job postings
    Input
    -----
    divs: bs4 tag
        contents of the Indeed job search results
    Output
    -----
        return titles of the jobs, companies' names, locations and job summary links of the companies from
        indeed job postings
    """
    # Get the title and summary link of the job
    job_titles = []
    summary_links = []
    names = []
    job_locations = []
    for div in divs:
        for a in div.find_all('a', attrs={'data-tn-element': 'jobTitle'}):
            job_titles.append(a['title'])
            summary_links.append(a['href'])
        # Get Company Name
        for sjcl in div.find_all('div', attrs={'class': 'sjcl'}):
            for name in sjcl.find_all('a', attrs={'data-tn-element': 'companyName'}):
                names.append(name.text)
        # Get company locations
        for loc in div.find_all('span', attrs={'class': 'location accessible-contrast-color-location'}):
            job_locations.append(loc.text)
        # Get the location of the job
        jobs_loc = []
        # for locs in divs:
        #     for loc in locs.find_all('span', attrs={'class': 'location accessible-contrast-color-location'}):
        #         # print(loc['data-rc-loc'])
        #         # jobs_loc.append(loc['data-rc-loc'])
        #         print(loc.text)
    return job_titles, summary_links, names, job_locations


# job_titless, summary_linkss, namess, locations = getJobInfo(divs)


##
# Job Summary link
def get_jobdes(summary_links, base_web='https://www.indeed.com'):
    """Get job descriptions from Indeed
    Input:
    -----
    summary_links: list-like
        list of connecting links
    base_web: www.indeed.com
    Output:
    -----
        Return a list-like of jobdescriptions for each link provided"""
    summaries = []
    for tail in summary_links:
        link = base_web + tail
        page = requests.get(link)
        soup = BeautifulSoup(page.text, 'html.parser')
        div = soup.find_all('div', attrs={'id': 'jobDescriptionText'})
        summaries.append(div[0].text)
    return summaries


# summaries = get_jobdes(summary_linkss)
# import re
# re.sub(r"\[\n\n|\n\n|\n\n\]",' ', test)

## Execute Web Scraping
if __name__ == '__main__':
    start = time.time()
    # Import url
    # If a link was provided
    if args['link']:
        URL = args['link']
    else:
        URL = 'https://www.indeed.com/jobs?q=Data+Scientist&l=Texas&explvl=entry_level'
    # get the html page using the URL specified above
    if args['page']:
        try:
            iter = 0
            page = requests.get(URL)

            # Specifying the desired format of 'page' using html parser.
            # This allows python to read various components of the page,
            # rather than treating it as one long string.
            print('[INFO] Getting information from the provided URL...')
            soup = BeautifulSoup(page.text, 'html.parser')
            # Get job information from job postings
            # Loop through tag to get all the job postings in a page
            posting_tag = "jobsearch-SerpJobCard unifiedRow row result clickcard"
            divs = soup.find_all('div', attrs={'data-tn-component': 'organicJob'})
            print('[INFO] The number of job postings on this page is:')
            jobs_per_page = len(divs)
            print(len(divs))  # 10 job postings per page

            job_titles, summary_links, names, locations = getJobInfo(divs)
            summaries = get_jobdes(summary_links)
            print('[INFO] all information scrapped, preparing to write to a csv file ...')
            # Putting all information into a csv file
            job_postings = {'Company Name': names,
                            'Title': job_titles,
                            'Job Location': locations,
                            'Job Description': summaries}
            Jobs = pd.DataFrame(job_postings)
            iter += 1
            while 0 < iter <= int(args['page']):
                URL_more = URL + '&start={}'.format(iter * jobs_per_page)
                page = requests.get(URL_more)

                # Specifying the desired format of 'page' using html parser.
                # This allows python to read various components of the page,
                # rather than treating it as one long string.
                print(
                    f'[INFO] Getting information from the provided URL starting at {iter * jobs_per_page} job posting...')
                soup = BeautifulSoup(page.text, 'html.parser')
                # Get job information from job postings
                # Loop through tag to get all the job postings in a page
                posting_tag = "jobsearch-SerpJobCard unifiedRow row result clickcard"
                divs = soup.find_all('div', attrs={'data-tn-component': 'organicJob'})
                print('[INFO] The number of job postings per page is:')
                print(len(divs))  # 10 job postings per page

                job_titles, summary_links, names, locations = getJobInfo(divs)
                summaries = get_jobdes(summary_links)
                # print('[INFO] all information scrapped, preparing to write to a csv file ...')
                # Putting all information into a csv file
                job_postings = {'Company Name': names,
                                'Title': job_titles,
                                'Job Location': locations,
                                'Job Description': summaries}
                Jobss = pd.DataFrame(job_postings)
                Jobs = pd.concat([Jobs, Jobss], ignore_index=True)
                iter += 1
        except Exception as e:
            print('Error occurs:')
            print(e)

        print('[INFO] Here\'s the first five jobs')
        print(Jobs.head())
        print('[INFO] The number of job postings is:', Jobs.shape[0])
        input = input('Do you want to continue?')
        input = input.lower()
        if input == 'y' or 'yes':
            if args['file']:
                Jobs.to_csv('{}.csv'.format(args['file']), header=True, index=None)
            else:
                Jobs.to_csv('Jobs.csv', header=True, index=None)
        else:
            print('[INFO] exit file without saving ...')
            pass
    else:
        try:
            page = requests.get(URL)

            # Specifying the desired format of 'page' using html parser.
            # This allows python to read various components of the page,
            # rather than treating it as one long string.
            print('[INFO] Getting information from the provided URL...')
            soup = BeautifulSoup(page.text, 'html.parser')
            # Get job information from job postings
            # Loop through tag to get all the job postings in a page
            posting_tag = "jobsearch-SerpJobCard unifiedRow row result clickcard"
            divs = soup.find_all('div', attrs={'data-tn-component': 'organicJob'})
            print('[INFO] The number of job postings per page is:')
            print(len(divs))  # 10 job postings per page

            job_titles, summary_links, names, locations = getJobInfo(divs)
            summaries = get_jobdes(summary_links)
            print('[INFO] all information scrapped, preparing to write to a csv file ...')
            # Putting all information into a csv file
            job_postings = {'Company Name': names,
                            'Title': job_titles,
                            'Job Location': locations,
                            'Job Description': summaries}
            Jobs = pd.DataFrame(job_postings)
            print('[INFO] Here\'s the first five job')
            print(Jobs.head())
            input = input('Do you want to continue?')
            input = input.lower()
            if input == 'y' or 'yes':
                if args['file']:
                    Jobs.to_csv('{}.csv'.format(args['file']), header=True, index=None)
                else:
                    Jobs.to_csv('Jobs.csv', header=True, index=None)
            else:
                print('[INFO] exit file without saving ...')
                pass
        except Exception as e:
            print('Error occurs:')
            print(e)
    end = time.time()
    print(f'[INFO] The execution time is {(end - start) / 60} minutes')