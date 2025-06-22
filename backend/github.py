"""
GitHub API service for Beth's unified assistant.
Handles repository management, issue tracking, and code analysis.
"""

import os
import requests
from typing import List, Dict, Optional, Any
import logging
from urllib.parse import urljoin
import base64
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GitHubService:
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("GITHUB_TOKEN not found in environment variables")
        
        self.base_url = "https://api.github.com/"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }
        
        self.username = None  # Will be populated on first API call
    
    async def test_connection(self):
        """Test the GitHub API connection."""
        try:
            # Try to get user info - simple API call to test connection
            url = urljoin(self.base_url, "user")
            response = requests.get(url, headers=self.headers)
            if response.status_code != 200:
                raise Exception(f"API returned status {response.status_code}")
            return True
        except Exception as e:
            logger.error(f"GitHub connection test failed: {e}")
            raise e
    
    def get_authenticated_user(self) -> Dict:
        """Get information about the authenticated user."""
        try:
            url = urljoin(self.base_url, "user")
            response = requests.get(url, headers=self.headers)
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'GitHub API error: {response.status_code}',
                    'details': response.text
                }
            
            user_data = response.json()
            self.username = user_data.get('login')
            
            return {
                'success': True,
                'user': {
                    'login': user_data.get('login'),
                    'name': user_data.get('name'),
                    'email': user_data.get('email'),
                    'bio': user_data.get('bio'),
                    'public_repos': user_data.get('public_repos'),
                    'private_repos': user_data.get('total_private_repos'),
                    'followers': user_data.get('followers'),
                    'following': user_data.get('following')
                }
            }
            
        except Exception as e:
            logger.error(f"Get authenticated user error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_user_repositories(self, sort: str = 'updated', per_page: int = 100) -> Dict:
        """Get all repositories for the authenticated user."""
        try:
            url = urljoin(self.base_url, "user/repos")
            params = {
                'sort': sort,
                'per_page': per_page,
                'type': 'all'
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'GitHub API error: {response.status_code}',
                    'details': response.text
                }
            
            repos_data = response.json()
            
            formatted_repos = []
            for repo in repos_data:
                formatted_repo = {
                    'name': repo.get('name'),
                    'full_name': repo.get('full_name'),
                    'description': repo.get('description'),
                    'url': repo.get('html_url'),
                    'clone_url': repo.get('clone_url'),
                    'ssh_url': repo.get('ssh_url'),
                    'private': repo.get('private'),
                    'language': repo.get('language'),
                    'size': repo.get('size'),
                    'stargazers_count': repo.get('stargazers_count'),
                    'forks_count': repo.get('forks_count'),
                    'created_at': repo.get('created_at'),
                    'updated_at': repo.get('updated_at'),
                    'pushed_at': repo.get('pushed_at'),
                    'default_branch': repo.get('default_branch')
                }
                formatted_repos.append(formatted_repo)
            
            return {
                'success': True,
                'repositories': formatted_repos,
                'count': len(formatted_repos)
            }
            
        except Exception as e:
            logger.error(f"Get user repositories error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_repository_details(self, owner: str, repo: str) -> Dict:
        """Get detailed information about a specific repository."""
        try:
            url = urljoin(self.base_url, f"repos/{owner}/{repo}")
            response = requests.get(url, headers=self.headers)
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'GitHub API error: {response.status_code}',
                    'details': response.text
                }
            
            repo_data = response.json()
            
            formatted_repo = {
                'name': repo_data.get('name'),
                'full_name': repo_data.get('full_name'),
                'description': repo_data.get('description'),
                'url': repo_data.get('html_url'),
                'clone_url': repo_data.get('clone_url'),
                'ssh_url': repo_data.get('ssh_url'),
                'private': repo_data.get('private'),
                'language': repo_data.get('language'),
                'languages_url': repo_data.get('languages_url'),
                'size': repo_data.get('size'),
                'stargazers_count': repo_data.get('stargazers_count'),
                'watchers_count': repo_data.get('watchers_count'),
                'forks_count': repo_data.get('forks_count'),
                'open_issues_count': repo_data.get('open_issues_count'),
                'created_at': repo_data.get('created_at'),
                'updated_at': repo_data.get('updated_at'),
                'pushed_at': repo_data.get('pushed_at'),
                'default_branch': repo_data.get('default_branch'),
                'topics': repo_data.get('topics', [])
            }
            
            return {
                'success': True,
                'repository': formatted_repo
            }
            
        except Exception as e:
            logger.error(f"Get repository details error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_repository_issues(self, owner: str, repo: str, state: str = 'all', 
                            labels: List[str] = None, per_page: int = 100) -> Dict:
        """Get issues for a specific repository."""
        try:
            url = urljoin(self.base_url, f"repos/{owner}/{repo}/issues")
            params = {
                'state': state,
                'per_page': per_page
            }
            
            if labels:
                params['labels'] = ','.join(labels)
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'GitHub API error: {response.status_code}',
                    'details': response.text
                }
            
            issues_data = response.json()
            
            formatted_issues = []
            for issue in issues_data:
                # Skip pull requests (they appear in issues API)
                if issue.get('pull_request'):
                    continue
                
                formatted_issue = {
                    'number': issue.get('number'),
                    'title': issue.get('title'),
                    'body': issue.get('body'),
                    'state': issue.get('state'),
                    'url': issue.get('html_url'),
                    'user': issue.get('user', {}).get('login'),
                    'assignees': [a.get('login') for a in issue.get('assignees', [])],
                    'labels': [l.get('name') for l in issue.get('labels', [])],
                    'created_at': issue.get('created_at'),
                    'updated_at': issue.get('updated_at'),
                    'closed_at': issue.get('closed_at'),
                    'comments': issue.get('comments')
                }
                formatted_issues.append(formatted_issue)
            
            return {
                'success': True,
                'issues': formatted_issues,
                'count': len(formatted_issues)
            }
            
        except Exception as e:
            logger.error(f"Get repository issues error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_repository_commits(self, owner: str, repo: str, since: str = None, 
                             per_page: int = 100) -> Dict:
        """Get recent commits for a repository."""
        try:
            url = urljoin(self.base_url, f"repos/{owner}/{repo}/commits")
            params = {'per_page': per_page}
            
            if since:
                params['since'] = since
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'GitHub API error: {response.status_code}',
                    'details': response.text
                }
            
            commits_data = response.json()
            
            formatted_commits = []
            for commit in commits_data:
                commit_data = commit.get('commit', {})
                formatted_commit = {
                    'sha': commit.get('sha'),
                    'message': commit_data.get('message'),
                    'author': {
                        'name': commit_data.get('author', {}).get('name'),
                        'email': commit_data.get('author', {}).get('email'),
                        'date': commit_data.get('author', {}).get('date')
                    },
                    'committer': {
                        'name': commit_data.get('committer', {}).get('name'),
                        'email': commit_data.get('committer', {}).get('email'),
                        'date': commit_data.get('committer', {}).get('date')
                    },
                    'url': commit.get('html_url'),
                    'stats': commit.get('stats', {})
                }
                formatted_commits.append(formatted_commit)
            
            return {
                'success': True,
                'commits': formatted_commits,
                'count': len(formatted_commits)
            }
            
        except Exception as e:
            logger.error(f"Get repository commits error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def create_issue(self, owner: str, repo: str, title: str, body: str = "", 
                    labels: List[str] = None, assignees: List[str] = None) -> Dict:
        """Create a new issue in a repository."""
        try:
            url = urljoin(self.base_url, f"repos/{owner}/{repo}/issues")
            
            data = {
                'title': title,
                'body': body
            }
            
            if labels:
                data['labels'] = labels
            if assignees:
                data['assignees'] = assignees
            
            response = requests.post(url, headers=self.headers, json=data)
            
            if response.status_code != 201:
                return {
                    'success': False,
                    'error': f'GitHub API error: {response.status_code}',
                    'details': response.text
                }
            
            issue_data = response.json()
            
            return {
                'success': True,
                'issue': {
                    'number': issue_data.get('number'),
                    'title': issue_data.get('title'),
                    'url': issue_data.get('html_url'),
                    'state': issue_data.get('state')
                },
                'message': f'Issue #{issue_data.get("number")} created successfully'
            }
            
        except Exception as e:
            logger.error(f"Create issue error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def search_repositories(self, query: str, sort: str = 'updated', 
                          per_page: int = 30) -> Dict:
        """Search for repositories."""
        try:
            url = urljoin(self.base_url, "search/repositories")
            params = {
                'q': query,
                'sort': sort,
                'per_page': per_page
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'GitHub API error: {response.status_code}',
                    'details': response.text
                }
            
            search_data = response.json()
            repos = search_data.get('items', [])
            
            formatted_repos = []
            for repo in repos:
                formatted_repo = {
                    'name': repo.get('name'),
                    'full_name': repo.get('full_name'),
                    'description': repo.get('description'),
                    'url': repo.get('html_url'),
                    'language': repo.get('language'),
                    'stargazers_count': repo.get('stargazers_count'),
                    'forks_count': repo.get('forks_count'),
                    'updated_at': repo.get('updated_at'),
                    'owner': repo.get('owner', {}).get('login')
                }
                formatted_repos.append(formatted_repo)
            
            return {
                'success': True,
                'repositories': formatted_repos,
                'total_count': search_data.get('total_count', 0),
                'count': len(formatted_repos),
                'query': query
            }
            
        except Exception as e:
            logger.error(f"Search repositories error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_file_content(self, owner: str, repo: str, path: str, ref: str = None) -> Dict:
        """Get the content of a file from a repository."""
        try:
            url = urljoin(self.base_url, f"repos/{owner}/{repo}/contents/{path}")
            params = {}
            
            if ref:
                params['ref'] = ref
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'GitHub API error: {response.status_code}',
                    'details': response.text
                }
            
            file_data = response.json()
            
            # Decode base64 content if it's a file
            content = None
            if file_data.get('encoding') == 'base64':
                try:
                    content = base64.b64decode(file_data.get('content', '')).decode('utf-8')
                except UnicodeDecodeError:
                    # Binary file, return raw base64
                    content = file_data.get('content', '')
            
            return {
                'success': True,
                'file': {
                    'name': file_data.get('name'),
                    'path': file_data.get('path'),
                    'sha': file_data.get('sha'),
                    'size': file_data.get('size'),
                    'url': file_data.get('html_url'),
                    'download_url': file_data.get('download_url'),
                    'type': file_data.get('type'),
                    'content': content,
                    'encoding': file_data.get('encoding')
                }
            }
            
        except Exception as e:
            logger.error(f"Get file content error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_recent_activity(self, days: int = 7) -> Dict:
        """Get recent activity across user's repositories."""
        try:
            # Get user info first
            user_result = self.get_authenticated_user()
            if not user_result['success']:
                return user_result
            
            username = user_result['user']['login']
            
            # Get recent repositories
            repos_result = self.get_user_repositories(sort='updated', per_page=10)
            if not repos_result['success']:
                return repos_result
            
            recent_activity = []
            cutoff_date = datetime.now() - timedelta(days=days)
            
            for repo in repos_result['repositories'][:5]:  # Check top 5 most recently updated
                # Get recent commits
                since_date = cutoff_date.isoformat()
                commits_result = self.get_repository_commits(
                    username, repo['name'], since=since_date, per_page=10
                )
                
                if commits_result['success']:
                    for commit in commits_result['commits']:
                        activity_item = {
                            'type': 'commit',
                            'repository': repo['name'],
                            'message': commit['message'],
                            'date': commit['author']['date'],
                            'url': commit['url']
                        }
                        recent_activity.append(activity_item)
            
            # Sort by date (newest first)
            recent_activity.sort(key=lambda x: x['date'], reverse=True)
            
            return {
                'success': True,
                'activity': recent_activity[:20],  # Return top 20 items
                'count': len(recent_activity[:20]),
                'days': days
            }
            
        except Exception as e:
            logger.error(f"Get recent activity error: {str(e)}")
            return {'success': False, 'error': str(e)}

# Global instance
github_service = GitHubService()

# Convenience functions for main.py
def get_github_repos() -> Dict:
    return github_service.get_user_repositories()

def search_github_repos(query: str) -> Dict:
    return github_service.search_repositories(query)

def get_github_repo_details(owner: str, repo: str) -> Dict:
    return github_service.get_repository_details(owner, repo)

def get_github_issues(owner: str, repo: str, state: str = 'open') -> Dict:
    return github_service.get_repository_issues(owner, repo, state)

def create_github_issue(owner: str, repo: str, title: str, body: str = "", 
                       labels: List[str] = None) -> Dict:
    return github_service.create_issue(owner, repo, title, body, labels)

def get_recent_github_activity(days: int = 7) -> Dict:
    return github_service.get_recent_activity(days)
