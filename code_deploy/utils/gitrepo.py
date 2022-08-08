# coding:utf-8
__author__ = "zhou"
# create by zhou on 2021/7/29
import requests
import gitlab
import time
import os
import sys
_ = os.path.abspath(os.path.join(os.path.dirname(__file__),"..",'..'))
sys.path.append(_)
import config

PROXY = getattr(config, 'PROXY', None)
TIMEOUT = 7


class GitPlatform(object):
    "基类"
    def __init__(self, token, server_url):
        self.token = token
        self.server_url = server_url
        self.proxy = PROXY

    def get_all_repos(self):
        pass


    def get_recent_versions(self, repo_id):
        pass


class GitLab(GitPlatform):
    "Gitlab"
    def __init__(self, token, server_url):
        GitPlatform.__init__(self, token, server_url)
        self.gl = None
        #self.proxy = PROXY
        self._valid()


    def _valid(self):
        if not self.proxy:
            self.gl = gitlab.Gitlab(self.server_url, private_token=self.token, timeout=TIMEOUT)
        else:
            self.session = requests.Session()
            self.session.proxies = {
                "https": self.proxy,
                "http": self.proxy,
            }
            print("Session",self.session)
            self.gl = gitlab.Gitlab(self.server_url, private_token=self.token, timeout=TIMEOUT,
                                    session=self.session)
        self.gl.auth()


    def get_all_repos(self):
        result = []
        for page in range(1, 5):
            projects = self.gl.projects.list(per_page=100,page=page)
            for project in projects:
                info = project.attributes
                url = info['ssh_url_to_repo']
                mapper = getattr(config, 'GIT_SSH_HOST_MAPPER', {})
                for i,j in mapper.items():
                    if i in url:
                        url = url.replace(i,j)
                        break
                result.append({'id': info['id'],
                               'namespace': info['name_with_namespace'],
                               'url': url})
            if len(projects) < 100:
                break
        return result

    def get_all_branches(self, repo_id):
        # 获取所有分支
        proj = self.gl.projects.get(repo_id)
        return [i.name for i in  proj.branches.list()]


    def get_recent_versions(self, repo_id, branch='master'):
        # 获取某分支的最近提交记录
        proj = self.gl.projects.get(repo_id)
        #print(dir(proj), proj.branches.list())
        commits = proj.commits.list(per_page=60,
                               query_parameters={'ref_name': branch},
                                    #all=True
        )
        # print(commits)
        commit_info = [commit.attributes for commit in commits]
        results = []
        for i in commit_info:
            results.append({'version': i['short_id'],
                            'message': i['message'].strip(),
                            'author': i['committer_name'],
                            'author_date': i['authored_date'].replace("T",' ')[:19]
                            })
        return results







class Gitee(GitPlatform):
    "Gitee"

    def __init__(self, token, server_url='https://gitee.com'):
        GitPlatform.__init__(self, token, server_url=server_url)
        self.gl = None
        self._valid()

    def _http_get(self, path):
        content = ''
        try:
            if self.proxy:
                proxies = {
                    "https": self.proxy,
                    "http": self.proxy,
                }
            else:
                proxies = None
            info = requests.get("%s%s" % (self.server_url, path),
                                headers={"Content-Type": "application/json;charset=UTF-8"}
                                ,timeout=TIMEOUT, proxies=proxies)
            #print(info.status_code)
            res = info.json()
            content = info.text
            assert info.status_code == 200
        except Exception as e:
            raise Exception("Gitee http get failed! %s" % content[:70])
        return  res


    def _valid(self):
        self._http_get("/api/v5/user?access_token=%s" % ( self.token),
                            )
        #print(info)

    def get_all_repos(self):
        result = []
        for i in range(1,5):
            res = self._http_get('/api/v5/user/repos?access_token=%s&sort=created&direction=desc&page=%s&per_page=100'
                           % (self.token, i))

            for repo in res:
                #print(repo)
                result.append({'id': repo['id'],
                                'namespace': repo['namespace']['path'] + "/" + repo['path'],
                                'url': repo['ssh_url']})
            #print(res)

            if len(res) <= 100:
                break
        return result


    def get_all_branches(self, repo_id):
        #result = []
        repos = self.get_all_repos()
        result = []
        for repo in repos:
            id = repo['id']
            namespace = repo['namespace']
            # url = repo['url']
            if id == int(repo_id):
                _a, _b = namespace.split("/")
                branchs = self._http_get("/api/v5/repos/%s/%s/branches?access_token=%s" %
                                     (_a,_b,self.token,))
                result = [i['name'] for i in branchs]
        return result
        #proj = self.gl.projects.get(repo_id)
        #return [i.name for i in  proj.branches.list()]


    def get_recent_versions(self, repo_id, branch='master'):
        repos = self.get_all_repos()
        result = []
        for repo in repos:
            id = repo['id']
            namespace = repo['namespace']
            # url = repo['url']
            if id == int(repo_id):
                _a, _b = namespace.split("/")
                print(time.time())
                commits = self._http_get("/api/v5/repos/%s/%s/commits?access_token=%s&page=1&per_page=60&sha=%s" %
                                     (_a,_b,self.token, branch))
                print(time.time())
                for commit in commits:
                    #print(commit)
                    try:
                        result.append({
                            'version': commit['sha'][:8],
                            'message': commit['commit']['message'].strip(),
                            'author':  commit['commit']['author']['name'],
                            'author_date': commit['commit']['author']['date'].replace("T", ' ')[:19]
                        })
                    except:
                        pass
                return result
        else:
            raise Exception("repo_id %s is error! it is an invalid value!" % repo_id)




if __name__ == '__main__':
    import time
    gl = GitLab('', 'http://192.168.2.131:7070')
    print(gl.get_all_branches(172))
    b = gl.get_recent_versions(172,branch='dev')
    print(b)