# DevSecOps CI Security Pipeline

A small, portfolio-ready Python service that demonstrates a practical security pipeline without making every scanner do the same work.

```
Developer push / pull request
              |
     +--------+---------+-----------------+----------------+----------------+
     |        |         |                 |                |                |
 Quality  Gitleaks   CodeQL SAST     Checkov IaC     Build + Trivy   Dependency review*
     |        |         |                 |                |                |
     +--------+---------+-----------------+----------------+----------------+
                                      |
                                Security gate
                                      |
                            Pass / fail + SARIF artifacts

* Pull requests only; Dependabot monitors dependencies continuously.
```

## What is included

| Control | Responsibility | Gate |
| --- | --- | --- |
| Ruff + pytest | Python correctness and code quality | Any lint or test failure |
| Gitleaks | Secrets committed now or in Git history | Any detected secret |
| CodeQL | Semantic Python SAST (`security-extended`) | Error-level or CVSS 7.0+ result |
| Checkov | Terraform configuration controls | Any selected baseline-control failure |
| Dependabot | Ongoing advisory monitoring and update PRs | Continuous monitoring |
| Dependency Review | Newly introduced dependency risk on a PR | High/critical vulnerability or denied license |
| Trivy | Built Docker image OS and library CVEs | Fixed critical vulnerability |

This separation is intentional: Gitleaks owns secrets, CodeQL owns source-code data flow, Checkov owns IaC policy, Trivy owns the resulting container image, and dependency tooling owns package advisories. Trivy is not used as an additional source or IaC scanner.

## Project layout

```
src/demo_app/                 Small Flask application
tests/                        Unit tests
terraform/                    Secure S3 Terraform example
.github/workflows/ci.yml      Push/PR/manual trigger
.github/workflows/reusable-security.yml
                              Reusable test, scan, report, and gate workflow
.github/codeql/               Baseline and training CodeQL configurations
.github/dependabot.yml        Scheduled dependency/action/IaC updates
security-demos/               Isolated, harmless intentional findings
```

## Run the app and quality checks locally

Python 3.11+ is required.

```bash
python -m pip install -e ".[dev]"
python -m ruff check src tests
python -m pytest -q
python -m flask --app demo_app.app:app run --port 8080
```

Then open `http://127.0.0.1:8080/` or call `GET /health`.

To build the production-shaped image locally:

```bash
docker build -t devsecops-demo:local .
docker run --rm -p 8080:8080 devsecops-demo:local
```

The image has no application secret, uses a supported slim Python image, and runs as an unprivileged user.

## GitHub setup

1. Create a GitHub repository, push this project, and make `main` the default branch.
2. In **Settings → Code security and analysis**, enable Dependabot alerts and Dependabot security updates. The supplied `dependabot.yml` also schedules version-update PRs for Python, Docker, Terraform, and Actions.
3. For an organization repository, add the free `GITLEAKS_LICENSE` repository secret if Gitleaks requires it for your account tier. Personal repositories do not require it.
4. In **Settings → Rules → Rulesets**, require the `Security gate` check for `main`.
5. Also require CodeQL code-scanning results with **High or higher** security alerts. That GitHub-side merge rule protects PRs even if the CodeQL workflow is changed. Code scanning for private repositories requires the applicable GitHub plan/Code Security entitlement.

The workflow deliberately uses only `GITHUB_TOKEN`; it does not need cloud credentials or a registry push. It grants `security-events: write` solely so SARIF results can appear in GitHub Code Scanning.

## Reports and evidence

Each execution leaves useful evidence:

- CodeQL uploads its results to Code Scanning and retains the generated SARIF for 30 days.
- Checkov and Trivy upload SARIF to Code Scanning and preserve matching workflow artifacts for 30 days, including failures.
- Gitleaks creates a redacted SARIF artifact and a job summary through its official action.
- Dependabot alerts and dependency-review results are kept by GitHub rather than a duplicate third-party SCA report.

Artifacts deliberately contain scanner metadata and locations, not unredacted secret values. Do not download or share a Gitleaks artifact outside the security team unless you have reviewed it.

## Security policy choices

The baseline has intentionally narrow, explained gates so it is useful rather than noisy:

- Any secret or selected Terraform control violation stops the run.
- CodeQL blocks error-level results and security scores of 7.0 or above; the branch ruleset independently requires High+ CodeQL results.
- A PR cannot introduce high/critical known dependency vulnerabilities or GPL-3.0/AGPL-3.0 dependencies.
- Trivy blocks fixed critical image vulnerabilities. `ignore-unfixed: true` prevents an upstream, unavailable patch from permanently blocking development; revisit this exception policy periodically.

The Checkov baseline focuses on the controls illustrated by this module: encryption, versioning, access logging, and public-access blocking. In a real application, expand the `check` set or use a centrally reviewed Checkov policy bundle.

## Demonstrate failures safely

`security-demos/` contains fake, non-functional training data only. It is excluded from the normal scans so `main` remains a safe baseline. Never deploy or apply anything in this directory.

In GitHub Actions, select **DevSecOps CI → Run workflow**, set **demo_mode** to `true`, and run it. The result is expected to fail, demonstrating all controls:

| Fixture | Expected scanner result |
| --- | --- |
| `gitleaks/fake-secrets.env` | Synthetic-token finding |
| `codeql/insecure.py` | `eval` code-injection finding |
| `terraform/main.tf` | Public SSH security-group findings |
| `Dockerfile.insecure` | Vulnerable old Python image finding |
| `dependabot/requirements.txt` | Dependabot advisory/update PR for an unsupported dependency |

The synthetic Gitleaks token cannot authenticate with any service. It is there specifically to show a secret-scanning gate; do not replace it with an actual token.

To demonstrate the PR-only dependency gate, create a throwaway branch, add an intentionally outdated package to the application manifest, and open a PR. Dependency Review compares only the change introduced by that PR and should reject a new high/critical advisory; close the branch afterwards. The existing Dependabot fixture is never installed and is only for observing Dependabot alerts and update PRs.

## Reuse with another app

Keep `reusable-security.yml`, scanner configuration files, and the `security_gate` job. A caller workflow needs only:

```yaml
jobs:
  security:
    uses: ./.github/workflows/reusable-security.yml
    with:
      image_name: my-service
```

Adjust the Python install/test commands, CodeQL paths, Terraform directory, image build context, and the approved Checkov policy set for that application. Keep scanner ownership distinct and change a gate only with an explicit risk acceptance.

## Validation performed

- Ruff passed on `src` and `tests`.
- Pytest passed: 2 tests.
- Both GitHub Actions YAML files parsed successfully.
- Docker/Trivy, Checkov, and GitHub-hosted Action execution require a running Docker daemon or a pushed GitHub repository; they are configured for GitHub-hosted Ubuntu runners and should be the next execution target.
