import requests

# TODO: insert code to section out URLs from BOA output

# given Github URL from BOA output, scrape relevant data and return dictionary of values
# generalize to for loop for all URLs
def extract_info(github_URL):
    ret = {}
    # extract owner + repo name
    splits = github_URL.split("/")
    owner = splits[3]
    repo = splits[4]

    # # FIRST REQUEST ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    request_URL = "https://api.github.com/repos/" + owner + "/" + repo
    # PARAMS = {'page':1}
    # sending get request and saving the response as response object
    # r = requests.get(url = request_URL, params=PARAMS)
    r = requests.get(url = request_URL)
    # extracting data in json format
    data = r.json()

    # GET number of stars
    ret["num_stars"] = data['stargazers_count']

    # GET number of forks
    ret["num_forks"] = data['forks_count']

    # GET number of open issues
    ret["num_open_issues"] = data['open_issues_count']
    # can be categorized into categories - "bug", "refactoring", "enhancement", etc.

    # SECOND REQUEST ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    request_URL = "https://api.github.com/repos/" + owner + "/" + repo + "/contributors?per_page=1"
    r = requests.get(url = request_URL)
    # GET number of contributors
    # https://stackoverflow.com/questions/44347339/github-api-how-efficiently-get-the-total-contributors-amount-per-repository
    data = r.headers['Link']
    splits = data.split(">")
    splits = splits[1].split("=")
    ret["num_contributors"] = splits[-1]

    # # THIRD REQUEST ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    request_URL = "https://api.github.com/repos/" + owner + "/" + repo + "/issues?state=closed&per_page=1"
    r = requests.get(url = request_URL)

    # GET number of closed issues
    try:
        data = r.headers['Link']
        splits = data.split(">")
        splits = splits[1].split("=")
        ret["num_closed_issues"] = splits[-1]
    except:
        ret["num_closed_issues"] = 0

    # Gets the authors' usernames and number of followers from a given repo URL (note: some public repo URLs doesn't have username included in the link)
    list_of_authors = get_authors_info(owner,repo,ret["num_contributors"])
    ret["authors_info"] = [];
    for item in list_of_authors:
        num_of_contributions = get_contribution_last_year("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", item['username'])
        ret["authors_info"].append({
            'username' : item['username'],
            'metric' : {
                "num_of_contributions" : num_of_contributions,
                "num_of_followers" : item['num_followers']
            }
        })

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

def get_authors_info(owner, repo, num_contributors):
    list_of_author_info = []
    # based on the second request. 
    request_URL = "https://api.github.com/repos/" + owner + "/" + repo + "/contributors?per_page=" + num_contributors
    r = requests.get(url = request_URL)
    for item in r.json():
      username = item['url'].split('/')[-1]
      # do fetch request for the number of followers, for each author
      request_URL = item['followers_url']
      r = requests.get(url = request_URL)
      list_of_author_info.append({
          'username': username,
          'num_followers' : len(r.json())
          })
    
    return list_of_author_info

def main():
    # sample url, no need to add /tree/master, just added here for convenience of access
    github_URL = "https://github.com/ArchimedesCAD/Archimedes/tree/master/br.org.archimedes.core/src/br/org/archimedes/gui/model/Workspace.java"
    print(extract_info(github_URL))
    

if __name__ == "__main__":
    main()