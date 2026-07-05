# project-git-release-connector-gitea (WIP)

## Gitea Connector

This is sample Connector implementation for the project-git-release-core project. For the whole documentation, please
check the core project's README.md file.

## General Disclaimer

I'm not a Python developer... I'm doing this as a hobby, because I need something to create version and releases on
Gitea
for my home project on the self-hosted Gitea. Use at your own risk, the source is open. I do not take responsibility for
the damaged caused.

## About the project

The project is heavily inspired by the [release-please](https://github.com/googleapis/release-please) project. The goal
is to provide a similar flow to collect
changes based on conventional commit messages, and handle the releases.

Since the release-please is tied to the Github, it cannot be really used for Gitea, Bitbucket, Gitlab, etc. This gave
the idea to create a library, which can be used on a modular base, and can be freely extended by You, or anyone else.

Since my use case is to release project version in self-hosted environment (Release on Gitea using Argo Workflow), I
decided to go with Python.

## About the author

Well... I'm a Java software developer since November 2011. I worked in multiple domain (telco, retail, finance, etc.).
Technology side I started with Java EE, but went with Spring (Boot) for the last 10 Years, but I'm definitely not a
Python developer.

To implement the project, I used the Claude (Free Tier), please the [AI Disclaimer](#ai-disclaimer) for more
information.

## AI Disclaimer

As I mentioned above, I'm not a Python developer, hence I used Claude AI (Free Tier) to help in the creation of the
project.

Currently, for the project I did not generated any actual code block (as far as I remember). What I used the AI for:

* Helping in the generation of GIT commands
* Helping in the generation of Regex expression
* I asked about project structure
* I asked about Python best practices
* I used it for brainstorming
* Proofreading this README file :D

I tried to avoid to share whole project parts with AI, and I never gave access to use my project (no agentic AI was
involved)