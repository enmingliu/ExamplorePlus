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

    # first request
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
    ret["num_issues"] = data['open_issues_count']
    # can be categorized into categories - "bug", "refactoring", "enhancement", etc.

    # second request
    request_URL = "https://api.github.com/repos/" + owner + "/" + repo + "/contributors?per_page=1"
    r = requests.get(url = request_URL)

    # GET number of contributors
    # https://stackoverflow.com/questions/44347339/github-api-how-efficiently-get-the-total-contributors-amount-per-repository
    data = r.headers['Link']
    splits = data.split(">")
    splits = splits[1].split("=")
    ret["num_contributors"] = splits[-1]
    
    # return dictionary of values
    return ret

def main():
    # sample url
    github_URL = "https://github.com/ArchimedesCAD/Archimedes/tree/master/br.org.archimedes.core/src/br/org/archimedes/gui/model/Workspace.java"
    print(extract_info(github_URL))
    github_URL = "https://github.com/MIPS/cts/tree/master/tools/dx-tests/src/dxconvext/util/FileUtils.java"
    print(extract_info(github_URL))


if __name__ == "__main__":
    main()