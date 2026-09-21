# PR-Agent (kgforais1 fork)

PR-Agent is an open-source, AI-powered code review agent for pull requests across GitHub, GitLab, Bitbucket, Azure DevOps, Gitea, and local checkouts.

## About this repository

This tree is [`kgforais1/pr-agent-kgforais1`](https://github.com/kgforais1/pr-agent-kgforais1), a standalone checkout of PR-Agent maintained independently of upstream. Documentation, contributing paths, and security reporting on this repo describe **this fork**, not The-PR-Agent/pr-agent.

## Lineage & upstream

This repository is a **detached fork** of [The-PR-Agent/pr-agent](https://github.com/The-PR-Agent/pr-agent) (detached 2026-09-19). Pull requests are **not** opened upstream from this repo. A scheduled `upstream-sync-check` workflow tracks upstream changes; see repository issues and [AGENTS.md](./AGENTS.md) for fork safety rules.

## Table of Contents

- [Getting Started](#getting-started)
- [Why Use PR-Agent?](#why-use-pr-agent)
- [Features](#features)
- [See It in Action](#see-it-in-action)
- [How It Works](#how-it-works)
- [Documentation](#documentation)
- [Data Privacy](#data-privacy)
- [Contributing](#contributing)
- [Security](#security)

## Getting Started

> [!NOTE]
> **Upstream-published Docker images and GitHub Action.** Examples below reference Docker Hub (`pragent/pr-agent`, legacy `codiumai/pr-agent`) and `uses: the-pr-agent/pr-agent@main`. Those artifacts are published by **upstream**, not by this fork. This fork has not decided to publish its own images, Action, or PyPI package (see the packaging audit in [TODO.md](./TODO.md)). Build from this repository or pin upstream artifacts deliberately.

> [!NOTE]
> **Docker Hub namespace migration (upstream publishing history).** Releases `0.34.2` and later are published under [`pragent/pr-agent`](https://hub.docker.com/r/pragent/pr-agent). Older releases (up to and including `v0.31`) remain available at the legacy [`codiumai/pr-agent`](https://hub.docker.com/r/codiumai/pr-agent) namespace as a frozen archive — no new images are pushed there. Update any pinned `image:` / `docker pull` / `uses: docker://` references when upgrading to `0.34.2+`.

### Quick Start

#### 1. GitHub Action (upstream-published artifact)

Add automated PR reviews to your repository with a simple workflow file:

```yaml
# .github/workflows/pr-agent.yml
name: PR Agent
on:
  pull_request:
    types: [opened, synchronize]
jobs:
  pr_agent_job:
    runs-on: ubuntu-latest
    steps:
    - name: PR Agent action step
      uses: the-pr-agent/pr-agent@main
      env:
        OPENAI_KEY: ${{ secrets.OPENAI_KEY }}
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

[Full GitHub Action setup guide](docs/docs/installation/github.md#run-as-a-github-action)

#### 2. CLI Usage (Local Development)

Run PR-Agent locally. `pip install pr-agent` installs the **upstream** PyPI package (this fork has not published its own); prefer `uv sync` from this repository for a source checkout.

```bash
pip install pr-agent
export OPENAI_KEY=your_key_here
pr-agent --pr_url https://github.com/owner/repo/pull/123 review
```

[Complete CLI setup guide](docs/docs/usage-guide/automations_and_usage.md#local-repo-cli)

#### 3. Other Platforms

- [GitLab webhook setup](docs/docs/installation/gitlab.md)
- [BitBucket app installation](docs/docs/installation/bitbucket.md)
- [Azure DevOps setup](docs/docs/installation/azure.md)

## Why Use PR-Agent?

### Built for Real Development Teams

**Fast & Affordable**: Each tool (`/review`, `/improve`, `/ask`) uses a single LLM call (~30 seconds, low cost)

**Handles Any PR Size**: Our [PR Compression strategy](docs/docs/core-abilities/compression_strategy.md) effectively processes both small and large PRs

**Highly Customizable**: JSON-based prompting allows easy customization of review categories and behavior via [configuration files](pr_agent/settings/configuration.toml)

**Platform Agnostic**:

- **Git Providers**: GitHub, GitLab, BitBucket, Azure DevOps, Gitea
- **Deployment**: CLI, GitHub Actions, Docker, self-hosted, webhooks
- **AI Models**: OpenAI GPT, Anthropic Claude, Google Gemini, DeepSeek, Mistral, and any other model reachable through LiteLLM (Azure OpenAI, AWS Bedrock, Vertex AI, Databricks, OpenRouter, Ollama, and more) — see [Changing a model](docs/docs/usage-guide/changing_a_model.md)

**Open Source Benefits**:

- Full control over your data and infrastructure
- Customize prompts and behavior for your team's needs
- No vendor lock-in
- Community-driven development

## Features

See the current [feature and git provider support matrix](docs/docs/index.md#features) in the PR-Agent documentation.

⚠️ `/help_docs` is temporarily disabled since `v0.36.1` pending a fix for a credential-exposure issue ([#2445](https://github.com/The-PR-Agent/pr-agent/issues/2445) — upstream issue).

## See It in Action

Examples below link to **upstream demo PRs** on The-PR-Agent/pr-agent (they are not on this fork).

<h4><a href="https://github.com/the-pr-agent/pr-agent/pull/530">/describe</a> (upstream example)</h4>
<div align="center">
<p float="center">
<img src="docs/docs/assets/describe_new_short_main.webp" width="512" alt="/describe example">
</p>
</div>
<hr>

<h4><a href="https://github.com/the-pr-agent/pr-agent/pull/732#issuecomment-1975099151">/review</a> (upstream example)</h4>
<div align="center">
<p float="center">
<kbd>
<img src="docs/docs/assets/review_new_short_main.png" width="512" alt="/review example">
</kbd>
</p>
</div>
<hr>

<h4><a href="https://github.com/the-pr-agent/pr-agent/pull/732#issuecomment-1975099159">/improve</a> (upstream example)</h4>
<div align="center">
<p float="center">
<kbd>
<img src="docs/docs/assets/improve_new_short_main.webp" width="512" alt="/improve example">
</kbd>
</p>
</div>

<hr>

### Usage Examples

PR-Agent tools run as a comment on a PR or from the CLI. A few common ones:

```bash
# Comment on a PR (GitHub/GitLab/Bitbucket/…):
/describe
/review
/improve
/ask "What does this PR change?" # free-text Q&A about the PR

# Or locally via the CLI:
pr-agent --pr_url <PR_URL> review
```

See the [Tools docs](docs/docs/tools/index.md#usage-examples) for the full list of tools with example commands, and each tool's page for screenshots and options.

<hr>

## How It Works

The following diagram illustrates PR-Agent tools and their flow (asset from this repository's docs):

![PR-Agent Tools](docs/docs/assets/diagram-v0.9.webp)

## Documentation

User-facing documentation lives in this repository under [`docs/`](docs/README.md). Preview locally from the repo root:

```bash
pip install mkdocs-material mkdocs-glightbox
mkdocs serve -f docs/mkdocs.yml
```

Start at [docs/docs/index.md](docs/docs/index.md). See [CONTRIBUTING.md](./CONTRIBUTING.md) and [SECURITY.md](./SECURITY.md) for contributor and security policy on **this fork**.

## Data Privacy

### Self-hosted PR-Agent

- If you host PR-Agent with your OpenAI API key, it is between you and OpenAI. You can read their API data privacy policy here:
https://openai.com/enterprise-privacy

## Contributing

To contribute to **this fork**, read [CONTRIBUTING.md](./CONTRIBUTING.md). Pull requests target `kgforais1/pr-agent-kgforais1` only — do not open PRs against The-PR-Agent/pr-agent from this repository.

For local verification, run `PYTHONPATH=. uv run pytest` from the repository root; it discovers the unit-test suite under `tests/unittest` by default. End-to-end tests under `tests/e2e_tests` require provider credentials and should be invoked explicitly, for example `PYTHONPATH=. uv run pytest tests/e2e_tests/test_github_app.py`.

## Security

Report vulnerabilities privately through [this fork's GitHub security advisories](https://github.com/kgforais1/pr-agent-kgforais1/security/advisories/new). See [SECURITY.md](./SECURITY.md) for the full policy.
