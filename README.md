# spine-cicd-actions

Reusable GitHub Actions for CI/CD workflows across the Spine Docs organization.

## Available Actions

### DCO Check

Validates that all commits in a pull request have proper Developer Certificate of Origin (DCO) sign-off.

**GitHub Actions Usage:**

```yaml
name: DCO Check

on:
  pull_request:

jobs:
  check-dco:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
        with:
          fetch-depth: 0  # Required to check all commits in PR
      - uses: SPINE-Docs/spine-cicd-actions/dco@v1
```

**Pre-commit Hook Usage:**

```yaml
- repo: https://github.com/SPINE-Docs/spine-cicd-actions
  rev: v1
  hooks:
    - id: check-dco
      name: Check DCO sign-off
      entry: python3 dco/check-dco.py
      language: system
      stages: [commit-msg]
```

**What it checks:**
- All commits have a valid `Signed-off-by: Name <email>` line
- Provides helpful error messages if DCO is missing

### Check SPDX Headers

Validates that all Python source files contain required SPDX license headers.

**GitHub Actions Usage:**

```yaml
name: Check Headers

on:
  pull_request:
  push:
    branches: [main]

jobs:
  check-headers:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: SPINE-Docs/spine-cicd-actions/check-headers@v1
```

**Pre-commit Hook Usage:**

```yaml
- repo: https://github.com/SPINE-Docs/spine-cicd-actions
  rev: v1
  hooks:
    - id: check-headers
      name: Check SPDX headers
      entry: python3 check-headers/check-headers.py --fix
      language: system
      files: '^(src|test)/.*\.py$'
```

**What it checks:**
- Python files in `src/` and `test/` directories
- Requires both:
  - `# SPDX-License-Identifier: Apache-2.0`
  - `# Copyright (C) 2025, The Spine Docs organization and its contributors.`
- With `--fix` flag: Automatically adds missing headers

## Versioning

Actions are versioned using Git tags. Use `@v1` for the latest stable v1.x release, or pin to a specific version like `@v1.0.0`.

## License

Apache License 2.0 - See [LICENSE](LICENSE) for details.
