# Security Policy

PR-Agent is an open-source tool to help efficiently review and handle pull requests.

This document describes the security policy of the open-source PR-Agent project in **this fork** (`kgforais1/pr-agent-kgforais1`). It does not cover [Qodo](https://www.qodo.ai/), the separate commercial product that evolved out of the hosted Qodo Merge offering — for that, see Qodo's own security policy.

## PR-Agent Self-Hosted Solutions

When using PR-Agent with your OpenAI (or other LLM provider) API key, the security relationship is directly between you and the provider. PR-Agent does not send your code to any servers operated by the project.

Types of [self-hosted solutions](docs/docs/installation/index.md):

- Locally
- GitHub integration
- GitLab integration
- BitBucket integration
- Azure DevOps integration

## PR-Agent Supported Versions

This section outlines which versions of PR-Agent are currently supported with security updates.

> [!NOTE]
> **Upstream-published artifacts.** The Docker and GitHub Action examples below reference images and workflows published by **upstream** (`the-pr-agent/pr-agent`, `pragent/pr-agent`). This fork has not decided to publish its own images or Action. Pin upstream artifacts deliberately or build from this repository.

### Docker Deployment Options

#### Latest Version

For the most recent updates, use the latest **upstream** Docker image (built nightly by upstream, not this fork):

```yaml
uses: the-pr-agent/pr-agent@main
```

#### Specific Release Version

For a fixed version, you can pin your action to a specific release version. Browse [this fork's releases](https://github.com/kgforais1/pr-agent-kgforais1/releases) for tags cut from this repository; upstream release tags are listed on [The-PR-Agent/pr-agent releases](https://github.com/The-PR-Agent/pr-agent/releases) and correspond to upstream-published Docker images.

For example, to github action:

```yaml
steps:
  - name: PR Agent action step
    id: pragent
    uses: docker://pragent/pr-agent:0.41.0-github_action
```

Version tags are immutable — once published, `0.41.0-github_action` always resolves to the same image. Rolling tags such as `latest` and `github_action` are not; see the "Immutable releases and version tags" note on the [Installation page](docs/docs/installation/index.md).

#### Enhanced Security with Docker Digest

For maximum security, you can specify the Docker image using its digest. Resolve the digest for the version you want to pin:

```sh
docker buildx imagetools inspect pragent/pr-agent:0.41.0-github_action --format '{{.Manifest.Digest}}'
```

Then reference it instead of the tag:

```yaml
steps:
  - name: PR Agent action step
    id: pragent
    uses: docker://pragent/pr-agent@sha256:<digest>
```

Official Docker Hub release images also publish GitHub Artifact Attestations, so you can verify a pinned digest before using it (valid for **upstream-built** images):

```sh
gh attestation verify \
  "oci://index.docker.io/pragent/pr-agent@sha256:<digest>" \
  --repo The-PR-Agent/pr-agent
```

## Reporting a Vulnerability

We take the security of PR-Agent seriously. If you discover a security vulnerability in **this fork**, please report it privately through GitHub's private vulnerability reporting on this repository:

[**Report a vulnerability**](https://github.com/kgforais1/pr-agent-kgforais1/security/advisories/new)

Please include a description of the vulnerability, steps to reproduce, and the affected PR-Agent version.

Do not open a public issue for a security report — a public issue discloses the vulnerability before a fix is available.
