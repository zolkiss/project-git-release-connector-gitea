# project-git-release-connector-gitea (WIP)

## Gitea Connector

This is a sample Connector implementation for the project-git-release-core project. For the whole documentation,
please refer to the core project's README.md file.

## General Disclaimer

I'm not a Python developer... I'm doing this as a hobby, because I need something to create versions and releases on
Gitea for my home project on self-hosted Gitea. Use at your own risk, the source is open. I do not take
responsibility for any damage caused.

## About the project

The project is heavily inspired by the [release-please](https://github.com/googleapis/release-please) project. The
goal is to provide a similar flow for collecting changes based on conventional commit messages and handling
releases.

Since release-please is tied to GitHub, it cannot really be used for Gitea, Bitbucket, GitLab, etc. This led to the
idea of creating a library that can be used in a modular way, and can be freely extended by you or anyone else.

Since my use case is to release project versions in a self-hosted environment (releasing on Gitea using Argo
Workflow), I decided to go with Python.

## About the author

I've been a Java software developer since November 2011. I've worked in multiple domains (telco, retail, finance,
etc.). On the technology side, I started with Java EE, but have used Spring (Boot) for the last 10 years, though I'm
definitely not a Python developer.

To implement the project, I used Claude (Free Tier); please see the [AI Disclaimer](#ai-disclaimer) below for more
information.

## AI Disclaimer

As I mentioned above, I'm not a Python developer, hence I used Claude AI (Free Tier) to help in the creation of the
project.

Currently, for the project I did not generated any actual code blocks for this project (as far as I remember). What I
used AI for:

* Helping generate Git commands
* Helping generate regex expressions
* Asking about project structure
* Asking about Python best practices
* Brainstorming
* Proofreading this README file :D

I tried to avoid sharing whole project parts with the AI, and never gave it access to my project (no agentic AI was
involved).