# -*- coding: utf-8 -*-

import json
import uuid
import operator
import requests

# Wrapper for call github apis
class Github:

    def __init__(self, github_endpoint=None):
        self.github_endpoint = github_endpoint or "https://api.github.com"

    def _get_response(self, endpoint, method="GET", params={}, data={}, files={}, headers={}):
        x_request_id = str(uuid.uuid4())
        headers["X-Request-ID"] = x_request_id

        # print ('GITHUB_REQUEST\t%s\t%s\t%s' % (method, endpoint, {'params': params, 'data': data, 'files': files, 'headers': headers}))

        resp = getattr(requests, method.lower())(endpoint, params=params, data=data, files=files, headers=headers)

        # print ('GITHUB_RESPONSE\t%s\t%s\t%s' % (method, endpoint, {'X-Request-ID': x_request_id, 'status': resp.status_code, 'content': resp.content}))
        return resp

    def get_org_repositories(self, **kwargs):

        try:
            response = self._get_response(self.github_endpoint + "/orgs/" + str(kwargs["org"]) + "/repos?page=" + str(kwargs["page"]))
            if response.status_code == 200:
                return response.json()
            return []

        except Exception, err:
            print "Exception :", err
            return []

    def get_repo_contributors_statics(self, **kwargs):
        try:
            response = self._get_response(self.github_endpoint + "/repos/" + str(kwargs["owner"]) + "/" + str(kwargs["repo"]) + "/stats/contributors")
            if response.status_code == 200:
                return response.json()
            return []

        except Exception, err:
            print "Exception :", err
            return []


if __name__ == '__main__':
    org = raw_input("Enter Organization Name : ")
    n = int(raw_input("No of most popular repositories : "))
    m = int(raw_input("No of top committees : "))

    github = Github()

    output = []
    repositories = []
    most_n_popular_repo = []

    page_num = 1
    temp = github.get_org_repositories(org=org, page=page_num)

    # call get org reppo method till we get repositories
    while (len(temp) > 0):
        page_num = page_num + 1
        temp = github.get_org_repositories(org=org, page=page_num)
        if len(temp) > 0:
            repositories.extend(temp)

    # sorted repositories based on forks
    if repositories:
        sorted_repo = sorted(repositories, key=operator.itemgetter('forks'), reverse=True)

        for i in xrange(len(sorted_repo)):
            if i is n:
                break
            most_n_popular_repo.append(sorted_repo[i])
     
    # Get Repo contributors for n popular repos.       
    for i in most_n_popular_repo:
        top_m_contributors = []
        data = {
            "repo_name": i["name"],
            "committees": []
        }
        contributors = github.get_repo_contributors_statics(owner=org, repo=i["name"])

        if contributors:
            sorted_contributors = sorted(contributors, key=operator.itemgetter('total'), reverse=True)

            for i in xrange(len(sorted_contributors)):
                if i is m:
                    break
                d = {
                    'committee': sorted_contributors[i]["author"]["login"],
                    'commits': sorted_contributors[i]["total"]
                }
                top_m_contributors.append(d)

        data["committees"].extend(top_m_contributors)
        output.append(data)
    print output
