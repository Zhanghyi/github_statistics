import requests
import concurrent.futures

# Set your GitHub auth token here
auth_token = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Set the repository owner and name here
owner = "BUPT-GAMMA"
repo = "GammaGL"

# Make the initial request to get all stargazers
page = 1
stargazers = []
per_page = 100

if __name__ == '__main__':
    while True:
        print(f'page {page}')
        request_url = f"https://api.github.com/repos/{owner}/{repo}/stargazers?page={page}&per_page={per_page}"
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"token {auth_token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        response = requests.get(request_url, headers=headers)
        if response.status_code != 200:
            break
        stargazers += response.json()
        if len(response.json()) < per_page:  # GitHub returns up to 100 stargazers
            break
        page += 1


    # Define functions to retrieve an individual stargazer's organizations and company
    def get_user_organizations(stargazer):
        request_url = stargazer["organizations_url"]
        headers = {"Authorization": f"token {auth_token}"}
        response = requests.get(request_url, headers=headers)
        if response.status_code != 200:
            return []
        orgs = [org["login"] for org in response.json()]

        # Check user profile for company and add it to orgs list
        user_profile_request_url = stargazer["url"]
        user_profile_response = requests.get(user_profile_request_url, headers=headers)
        if user_profile_response.status_code == 200 and "company" in user_profile_response.json() and \
                user_profile_response.json()["company"]:
            orgs.append(user_profile_response.json()["company"])

        return orgs


    # Use a ThreadPoolExecutor to send multiple organization requests concurrently
    organizations = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(get_user_organizations, stargazer) for stargazer in stargazers]
        for future in concurrent.futures.as_completed(futures):
            organizations += future.result()

    # Get the counts of each organization
    org_counts = {}
    for org in organizations:
        if org in org_counts:
            org_counts[org] += 1
        else:
            org_counts[org] = 1

    # Sort the organization counts by amount and alphabetically
    org_counts_items = list(org_counts.items())
    org_counts_items.sort(key=lambda x: (-x[1], x[0]))

    # Print out the organization counts
    print("Organization and Company Counts:")
    for org, count in org_counts_items:
        print(f"{org}: {count}")
        
