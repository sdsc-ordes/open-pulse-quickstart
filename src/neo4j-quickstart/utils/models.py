"""Pydantic models for GitHub entities."""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from enum import Enum


class GitHubItemType(str, Enum):
    """Types of GitHub entities."""
    USER = "User"
    ORGANIZATION = "Organization"
    REPOSITORY = "Repository"


class UserModel(BaseModel):
    """Model representing a GitHub user."""
    name: str = ""
    id: int = 0
    type: GitHubItemType = GitHubItemType.USER

    # Repos the user owns
    owner_of: List[str] = Field(default_factory=list)
    # Repos the user has forked
    #forked_repositories: List[str] = Field(default_factory=list)
    #how do we get this info? 
    # Repos the user has contributed to
    contributor_of: List[str] = Field(default_factory=list)


class OrgModel(BaseModel):
    """Model representing a GitHub organization."""
    name: str = ""
    id: int = 0
    type: GitHubItemType = GitHubItemType.ORGANIZATION
    members: List[str] = Field(default_factory=list)

    # Org-owned repos that are original
    owner_of: List[str] = Field(default_factory=list)
    # Org-owned repos that are forks
    #forked_repositories: List[str] = Field(default_factory=list)
    # Org contributed repos
    contributor_of: List[str] = Field(default_factory=list)


class RepoModel(BaseModel):
    """Model representing a GitHub repository."""
    name: str = ""
    id: int = 0
    type: GitHubItemType = GitHubItemType.REPOSITORY
    contributors: List[str] = Field(default_factory=list)
    owner: str = ""

    # Fork information
    #is_fork: bool = False
    parent_of: List[str] = Field(default_factory=list)


class GraphData(BaseModel):
    users: Dict[str, UserModel] = Field(default_factory=dict)
    orgs: Dict[str, OrgModel] = Field(default_factory=dict)
    repos: Dict[str, RepoModel] = Field(default_factory=dict)

    def add_user(self, name: str, id_: int = 0) -> UserModel:
        if name not in self.users:
            self.users[name] = UserModel(name=name, id=id_)
        else:
            if id_:
                self.users[name].id = id_
        return self.users[name]

    def add_org(self, name: str, id_: int = 0) -> OrgModel:
        if name not in self.orgs:
            self.orgs[name] = OrgModel(name=name, id=id_)
        else:
            if id_:
                self.orgs[name].id = id_
        return self.orgs[name]

    def add_repo(self, name: str, id_: int = 0) -> RepoModel:
        if name not in self.repos:
            self.repos[name] = RepoModel(name=name, id=id_)
        else:
            if id_:
                self.repos[name].id = id_
        return self.repos[name]


# class GraphData(BaseModel):
#     """Holds references to users, orgs, and repos discovered."""
#     users: Dict[str, UserModel] = Field(default_factory=dict)
#     orgs: Dict[str, OrgModel] = Field(default_factory=dict)
#     repos: Dict[str, RepoModel] = Field(default_factory=dict)

#     def add_user(self, user: UserModel):
#         """Add a user to the graph."""
#         self.users[user.name] = user

#     def add_org(self, org: OrgModel):
#         """Add an organization to the graph."""
#         self.orgs[org.name] = org

#     def add_repo(self, repo: RepoModel):
#         """Add a repository to the graph."""
#         self.repos[repo.name] = repo

#     def has_user(self, name: str) -> bool:
#         """Check if user exists in graph."""
#         return name in self.users

#     def has_org(self, name: str) -> bool:
#         """Check if org exists in graph."""
#         return name in self.orgs

#     def has_repo(self, full_name: str) -> bool:
#         """Check if repo exists in graph."""
#         return full_name in self.repos

#     def get_user(self, name: str) -> Optional[UserModel]:
#         """Get a user by name."""
#         return self.users.get(name)

#     def get_org(self, name: str) -> Optional[OrgModel]:
#         """Get an org by name."""
#         return self.orgs.get(name)

#     def get_repo(self, full_name: str) -> Optional[RepoModel]:
#         """Get a repo by full name."""
#         return self.repos.get(full_name)