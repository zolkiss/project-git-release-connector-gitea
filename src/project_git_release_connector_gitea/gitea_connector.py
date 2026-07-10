from datetime import datetime
from logging import log
from typing import Any

import requests
from project_git_release.classes import GitReleasePR, GitRelease, CommitDetails, GitReleaseResponse, GitHashAndMsg
from project_git_release.core import Connector, ReleaseConfig
from requests import Response

from project_git_release_connector_gitea import log


class GiteaConnector(Connector):

    def __init__(self, config: ReleaseConfig):
        super().__init__(config)
        self.api_base_url = f"{config.url}/api/v1/repos/{config.owner}/{config.repo}"

    def __create_header(self) -> dict[str, str]:
        headers = {
            "Authorization": f"token {self.config.token}",
            "Accept": "application/json"
        }
        return headers

    def __get(self,
              url: str,
              msg_404: str = "Cannot find the requested resource",
              msg_err: str = "Error while requesting the resource") -> Response | None:
        headers = self.__create_header()

        log.debug("Calling url (GET): %s", url)
        response = requests.get(url, headers=headers)
        if 200 <= response.status_code <= 202:
            return response
        elif 404 == response.status_code:
            log.info(msg_404)
            return None
        else:
            log.error(msg_err)
            log.debug(response.content)
            return None

    def __post_json(self,
                    url: str,
                    request_body: dict,
                    msg_404: str = "Cannot find the requested resource",
                    msg_err: str = "Error while requesting the resource") -> Response | None:
        headers = self.__create_header()

        log.debug("Calling url (POST): %s", url)
        response = requests.post(url, json=request_body, headers=headers)
        if 200 <= response.status_code <= 202:
            return response
        elif 404 == response.status_code:
            log.info(msg_404)
            return None
        else:
            log.error(msg_err)
            log.debug(response.content)
            return None

    def __patch(self,
                url: str,
                request_body: dict,
                msg_404: str = "Cannot find the requested resource",
                msg_err: str = "Error while requesting the resource") -> Response | None:
        headers = self.__create_header()

        log.debug("Calling url (PATCH): %s", url)
        response = requests.patch(url, data=request_body, headers=headers)
        if 200 <= response.status_code <= 202:
            return response
        elif 404 == response.status_code:
            log.info(msg_404)
            return None
        else:
            log.error(msg_err)
            log.debug(response.content)
            return None

    def get_latest_release_pr(self, state: str) -> GitReleasePR | None:
        log.info(msg=f"Getting latest release PR")
        response = self.__get(
            url=f"{self.api_base_url}/pulls?base_branch={self.config.default_branch}&state={state}",
            msg_404=f"No pull requests can be found for repo {self.config.repo}",
            msg_err=f"Error while querying the pull requests for repo {self.config.repo}")

        if response is None:
            return None

        response_json = response.json()
        for data in response_json:
            if self.__validate_pr_response_state_and_head(data, state):
                return GitReleasePR(
                    id=data["id"],
                    number=data["number"],
                    title=data["title"],
                    commit_sha=data["merge_commit_sha"],
                    comment=data["body"],
                    merged=data["merged"]
                )
        return None

    def get_latest_release_prs(self, state: str, limit: int = 10) -> list[GitReleasePR]:
        log.info(msg=f"Getting latest release PRs")
        response = self.__get(
            url=f"{self.api_base_url}/pulls?base_branch={self.config.default_branch}&state={state}&limit={limit}",
            msg_404=f"No pull requests can be found for repo {self.config.repo}",
            msg_err=f"Error while querying the pull requests for repo {self.config.repo}")

        pull_requests = []
        if response is None:
            return pull_requests

        response_json = response.json()
        for data in response_json:
            if self.__validate_pr_response_state_and_head(data, state):
                pull_requests.append(GitReleasePR(
                    id=data["id"],
                    number=data["number"],
                    title=data["title"],
                    commit_sha=data["merge_commit_sha"],
                    comment=data["body"],
                    merged=data["merged"]
                ))
        return pull_requests

    def __validate_pr_response_state_and_head(self, data, state: str) -> Any:
        return (data["head"]["ref"] == self.config.release_branch
                and data["state"] == state)

    def create_release_pr(self, pull_request_title: str, pull_request_commit_text: str) -> GitReleasePR | None:
        log.info(msg=f"Creating release PR")
        request_body = {
            'base': self.config.default_branch,
            'head': self.config.release_branch,
            'title': pull_request_title,
            'body': pull_request_commit_text
        }

        response = self.__post_json(
            url=f"{self.api_base_url}/pulls",
            request_body=request_body,
            msg_404=f"No pull requests can be found for repo {self.config.repo}",
            msg_err=f"Error while querying the pull requests for repo {self.config.repo}")

        if response is None:
            return None

        data = response.json()
        return GitReleasePR(
            id=data["id"],
            number=data["number"],
            title=data["title"],
            commit_sha=data["merge_commit_sha"],
            comment=data["body"],
            merged=False
        )

    def update_release_pr(self, release_pr_number: int, pull_request_title: str,
                          pull_request_commit_text: str) -> GitReleasePR | None:
        log.info(msg=f"Updating release PR")
        request_body = dict()
        request_body["title"] = pull_request_title
        request_body["body"] = pull_request_commit_text
        response = self.__patch(
            url=f"{self.api_base_url}/pulls/{release_pr_number}",
            request_body=request_body,
            msg_404=f"No pull requests can be found for repo {self.config.repo}",
            msg_err=f"Error while querying the pull requests for repo {self.config.repo}")

        if response is None:
            return None

        data = response.json()
        return GitReleasePR(
            id=data["id"],
            number=data["number"],
            title=data["title"],
            commit_sha=data["merge_commit_sha"],
            comment=data["body"],
            merged=False
        )

    def get_latest_release(self) -> GitRelease | None:
        log.info("Getting the releases...")
        response = self.__get(
            url=f"{self.api_base_url}/releases",
            msg_404=f"Cannot find release for the repository",
            msg_err=f"Error while getting the latest release"
        )

        if response is None:
            return None

        response_json = response.json()
        for release in response_json:
            tag_name = release["tag_name"]
            log.info(f"Found the previous release: {tag_name}")
            log.debug(f"Current version prefix: '{self.config.release_version_prefix}'")

            if not self.validate_release_version(tag_name):
                log.info(
                    f"{tag_name} is not a valid SEMVER version (including prefix '{self.config.release_version_prefix}'). Validating the next one...")
                continue
            else:
                log.info(
                    f"The {tag_name} tag is a valid SEMVER version with prefix '{self.config.release_version_prefix}'")

            response_json = self.get_tag_details(tag_name)
            if response_json is None:
                return None

            commit_sha = response_json["commit"]["sha"]
            tag_message = response_json["message"]

            log.info(f"Commit SHA for version {tag_name}: {commit_sha}")

            return GitRelease(
                tag_name=tag_name,
                tag_message=tag_message,
                commit_sha=commit_sha
            )

        log.info("There is no release with valid version number.")
        return None

    def get_release_by_tag(self, tag: str) -> GitRelease | None:
        log.info("Getting the release for %s", tag)
        response = self.__get(
            url=f"{self.api_base_url}/releases/tags/{tag}",
            msg_404=f"Cannot find release for tag {tag}",
            msg_err=f"Error while getting the release for tag {tag}"
        )

        if response is None:
            return None

        release = response.json()
        tag_name = release["tag_name"]
        log.info(f"Found the release by tag {tag_name}")

        response_json = self.get_tag_details(tag_name)
        if response_json is None:
            return None

        commit_sha = response_json["commit"]["sha"]
        tag_message = response_json["message"]

        log.info(f"Commit SHA for version {tag_name}: {commit_sha}")

        return GitRelease(
            tag_name=tag_name,
            tag_message=tag_message,
            commit_sha=commit_sha
        )

    def get_tag_details(self, tag_name: str) -> dict | None:
        log.info(f"Getting the details of tag {tag_name}...")
        response = self.__get(
            url=f"{self.api_base_url}/tags/{tag_name}",
            msg_404=f"Cannot find the details for tag {tag_name}",
            msg_err=f"Error while getting the details for tag {tag_name}"
        )

        if response is None:
            return None

        return response.json()

    def get_commit_details(self, hash_and_msg: GitHashAndMsg) -> CommitDetails | None:
        log.info("Getting details for %s", hash_and_msg.hash)
        response = self.__get(
            url=f"{self.api_base_url}/git/commits/{hash_and_msg.hash}",
            msg_404=f"Cannot find details for the commit",
            msg_err=f"Error while getting details for the commit"
        )

        if response is None:
            return None

        response_json = response.json()
        commit_message = response_json["commit"]["message"].replace(hash_and_msg.message, "").strip()

        commit_message_parts: list[str] = commit_message.split("\n\n")
        if len(commit_message_parts) > 1:
            body = commit_message_parts[0].strip()
            footers = commit_message_parts[1:]
        else:
            body = commit_message
            footers = []

        return CommitDetails(
            hash=hash_and_msg.hash,
            title=hash_and_msg.message,
            creation_time=datetime.fromisoformat(response_json["created"]),
            body=body,
            footers=footers
        )

    def create_release(self, latest_unreleased_version: GitRelease, change_log: str, draft: bool = False,
                       pre_release: bool = False) -> GitReleaseResponse:
        log.info("Creating release for %s (%s)", latest_unreleased_version.tag_name,
                 latest_unreleased_version.commit_sha)

        request_body = {
            'body': change_log,
            'draft': draft,
            'name': latest_unreleased_version.tag_name,
            'prerelease': pre_release,
            'tag_message': latest_unreleased_version.tag_message,
            'tag_name': latest_unreleased_version.tag_name,
            'target_commitish': latest_unreleased_version.commit_sha
        }

        log.debug("Request body for release creation:\n%s", request_body)

        response = self.__post_json(
            url=f"{self.api_base_url}/releases",
            request_body=request_body,
            msg_404=f"Cannot find release endpoint",
            msg_err=f"Error while creating release for commit"
        )

        if response is None:
            return None

        data = response.json()
        return GitReleaseResponse(
            tag_name=data["tag_name"],
            name=data["name"],
            commit_sha=data["target_commitish"],
            id=data["id"],
            draft=data["draft"],
            pre_release=data["prerelease"]
        )
