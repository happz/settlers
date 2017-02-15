import collections
import github

import hlib.error

IssueComment = collections.namedtuple('IssueComment', ['user', 'body'])
Issue = collections.namedtuple('Issue', ['user', 'number', 'title', 'body', 'labels', 'comments'])

class Issue(object):
  def __init__(self, issue):
    super(Issue, self).__init__()

    self.user     = None
    self.number   = issue.number
    self.title    = issue.title
    self.body     = issue.body
    self.labels   = dict([(label.name, label) for label in issue.labels])
    self.comments = [IssueComment(comment.user.login, comment.body) for comment in issue.get_comments()]

class IssuesError(hlib.error.BaseError):
  def __init__(self, gh_error, **kwargs):
    kwargs['reply_status'] = 503

    if isinstance(gh_error, github.GithubException):
      kwargs['msg'] = '%(status)s - %(data)s'
      kwargs['params'] = {'status': gh_error.status, 'data': gh_error.data['message']}

    else:
      kwargs['msg'] = repr(gh_error)

    super(IssuesError, self).__init__(**kwargs)

class Repository(object):
  def __init__(self, token, repository_name):
    super(Repository, self).__init__()

    self.token = token
    self.repository_name = repository_name

    try:
      self.gh = github.Github(self.token, user_agent = 'hlib (https://github.com/happz/hlib)')
      self.user = self.gh.get_user()
      self.repository = self.user.get_repo(self.repository_name)

    except Exception, e:
      raise IssuesError(e)

  def get_issues(self):
    try:
      issues = []

      for issue in self.repository.get_issues():
        issues.append(Issue(issue))

    except Exception, e:
      raise IssuesError(e)

    return issues

  def create_new_issue(self, title, body):
    try:
      self.repository.create_issue(title, body = body)

    except Exception, e:
      raise IssuesError(e)
