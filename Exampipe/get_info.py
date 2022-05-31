import requests
import time
from calendar import timegm
from datetime import datetime
from pytz import timezone
import sys

# TODO: insert code to section out URLs from BOA output

# given Github URL from BOA output, scrape relevant data and return dictionary of values
# generalize to for loop for all URLs
def extract_info(github_URL):
    ret = {}
    # extract owner + repo name
    splits = github_URL.split("/")
    owner = splits[3]
    repo = splits[4]

    # insert Github API Access Token
    username = "nikkiwoo"
    api_token = "" # TODO

    # FIRST REQUEST ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # request_URL = "https://api.github.com/repos/" + owner + "/" + repo
    # # sending get request and saving the response as response object
    # r = requests.get(url = request_URL, auth=(username,api_token))
    # # extracting data in json format
    # data = r.json()

    # # GET number of stars
    # try:
    #     ret["num_stars"] = data['stargazers_count']
    # except KeyError:
    #     ret["num_stars"] = 0

    # # GET number of forks
    # ret["num_forks"] = data['forks_count']

    # # GET number of open issues
    # ret["num_open_issues"] = data['open_issues_count']
    # # can be categorized into categories - "bug", "refactoring", "enhancement", etc.

    # SECOND REQUEST ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    request_URL = "https://api.github.com/repos/" + owner + "/" + repo + "/contributors?per_page=1"
    r = requests.get(url = request_URL, auth=(username,api_token))
    # GET number of contributors
    # https://stackoverflow.com/questions/44347339/github-api-how-efficiently-get-the-total-contributors-amount-per-repository
    try:
        data = r.headers['Link']
        splits = data.split(">")
        splits = splits[1].split("=")
        ret["num_contributors"] = int(splits[-1])
    except KeyError:
        ret["num_contributors"] = 0
    

    # THIRD REQUEST ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    request_URL = "https://api.github.com/repos/" + owner + "/" + repo + "/issues?state=closed&per_page=1"
    r = requests.get(url = request_URL, auth=(username,api_token))

    # GET number of closed issues
    try:
        data = r.headers['Link']
        splits = data.split(">")
        splits = splits[1].split("=")
        ret["num_closed_issues"] = splits[-1]
    except KeyError:
        ret["num_closed_issues"] = 0

    # FOURTH REQUEST ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    request_URL = "https://api.github.com/repos/" + owner + "/" + repo + "/branches/master"
    r = requests.get(url = request_URL, auth=(username,api_token))

    # GET time of last commit
    data = r.json()
    last_commit = data['commit']['commit']['author']['date']
    # convert to UTC
    datetime_object = datetime.strptime(last_commit, "%Y-%m-%dT%H:%M:%SZ")
    converted = datetime_object.astimezone(timezone('UTC'))
    converted = converted.strftime("%Y-%m-%dT%H:%M:%SZ")
    utc_time = time.strptime(converted, "%Y-%m-%dT%H:%M:%SZ")
    epoch_time = timegm(utc_time)
    # add to dictionary
    ret["last_commit"] = epoch_time

    # Gets the authors' usernames and number of followers from a given repo URL (note: some public repo URLs doesn't have username included in the link)
    # list_of_authors = get_authors_info(owner,repo,api_token)
    # ret["authors_info"] = [];
    # for item in list_of_authors:
    #     num_of_contributions = get_contribution_last_year("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", item['username'])
    #     ret["authors_info"].append({
    #         'username' : item['username'],
    #         'metric' : {
    #             "num_of_contributions_last_yr" : num_of_contributions,
    #             "num_of_followers" : item['num_of_followers'],
    #             'num_of_contri_for_cur_repo' : item['num_of_contri_for_cur_repo']
    #         }
    #     })
    # return dictionary of values
    return ret


def get_contribution_last_year(api_key, username):
    # referenced https://gist.github.com/gbaman/b3137e18c739e0cf98539bf4ec4366ad.
    # need to have an API key for using GraphQL API to get the totalContributions
    headers = {"Authorization": "Bearer " + api_key}
    # variables used for passing parameters into the query
    variables = {
        "username": username
    }
    query = """
          query($username: String!) { 
              user(login: $username) {
                  name
                  contributionsCollection {
                    contributionCalendar {
                      colors
                      totalContributions
                      weeks {
                        contributionDays {
                          color
                          contributionCount
                          date
                          weekday
                        }
                        firstDay
                      }
                    }
                  }
                }
              }
          
          """
    request = requests.post('https://api.github.com/graphql', json={'query': query, 'variables': variables}, headers=headers)
    if request.status_code == 200 and isinstance(request.json(),type(None)) == False:
        return request.json()['data']['user']['contributionsCollection']['contributionCalendar']['totalContributions']
    else:
        return 0

def get_authors_info(owner, repo, api_key):
    headers = {'Authorization': 'token %s' % api_key}
    list_of_author_info = []
    # based on the second request. 
    request_URL = "https://api.github.com/repos/" + owner + "/" + repo + "/contributors?per_page=5"
    r = requests.get(url = request_URL, headers=headers)
    for item in r.json():
      username = item['url'].split('/')[-1]
      # do fetch request for the number of followers, for each author
      request_URL = item['followers_url']
      r = requests.get(url = request_URL, headers=headers)
      list_of_author_info.append({
          'username': username,
          'num_of_followers' : len(r.json()),
          'num_of_contri_for_cur_repo' : item['contributions']
          })
    
    return list_of_author_info

def main():
    # sample url, no need to add /tree/master, just added here for convenience of access
    # github_URL = "https://github.com/ArchimedesCAD/Archimedes/"
    print(extract_info(sys.argv[1]))
    

if __name__ == "__main__":
    main()