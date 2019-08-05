#!/usr/bin/env python
import os
from pathlib import Path
from github import Github

# make sure we have all the needed env vars
assert os.environ["DRONE_REPO"], "Ensure DRONE_REPO env var is set in form of 'owner/reponame'" # =[secret:owner]/[secret:repo]
assert os.environ["GITHUB_API_TOKEN"], "Cannot upload without a GITHUB_API_TOKEN env var set." # =[secret:repo_api_key]
assert os.environ["DRONE_COMMIT_REF"], "Missing DRONE_COMMIT_REF env var." #=refs/tags/0.1.5macexec1

# release tarball to upload
tarball = Path.cwd().joinpath('cli', 'dist', 'drone-deploy.x86_64-osx.tar.gz')
assert tarball.exists(), "Couldn't locate the release drone-deploy.x86_64-osx.tar.gz"

# get owner and repo from drone env var
drone_repo = os.environ["DRONE_REPO"].split("/")
owner_name = drone_repo[0]
repo_name = drone_repo[1]

# get tag from drone env var
tag_var = os.environ["DRONE_COMMIT_REF"].split("/")
tag = tag_var[2]

# get api key
token = os.environ["GITHUB_API_TOKEN"]

# get the release for the tag
g = Github(token)
repo = g.get_user().get_repo(repo_name)
release = repo.get_release(tag)

# add the tarball to the release
asset = release.upload_asset(str(tarball))
if asset.state == 'uploaded':
    print("uploaded release:")
    print("/t{asset.browser_download_url}")
else:
    assert False, "Failed to upload release."
