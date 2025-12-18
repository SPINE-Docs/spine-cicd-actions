#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2025, The Spine Docs organization and its contributors.

"""
Sync labels from the current repository to all downstream repositories listed in repos.yaml.
"""

import os
import sys
from pathlib import Path

import yaml
from github import Auth, Github, GithubException


def load_repos(repos_file: Path) -> list[str]:
    """Load the list of downstream repositories from repos.yaml."""
    with open(repos_file) as f:
        data = yaml.safe_load(f)
    return data.get("repos", [])


def get_labels(repo):
    """Get all labels from a repository."""
    labels = []
    for label in repo.get_labels():
        labels.append(
            {
                "name": label.name,
                "color": label.color,
                "description": label.description or "",
            }
        )
    return labels


def sync_labels_to_repo(source_labels: list[dict], target_repo, dry_run: bool = False):
    """Sync labels to a target repository."""
    print(f"\n{'=' * 60}")
    print(f"Syncing labels to: {target_repo.full_name}")
    print(f"{'=' * 60}")

    # Get existing labels in target repo
    existing_labels = {label.name: label for label in target_repo.get_labels()}

    created_count = 0
    skipped_count = 0
    error_count = 0

    for label_data in source_labels:
        label_name = label_data["name"]
        label_color = label_data["color"]
        label_description = label_data["description"]

        if label_name in existing_labels:
            print(f"  ✓ Label already exists: {label_name}")
            skipped_count += 1
        else:
            try:
                if dry_run:
                    print(f"  [DRY RUN] Would create label: {label_name}")
                else:
                    target_repo.create_label(
                        name=label_name, color=label_color, description=label_description
                    )
                    print(f"  ✓ Created label: {label_name}")
                created_count += 1
            except GithubException as e:
                print(f"  ✗ Failed to create label '{label_name}': {e.data.get('message', str(e))}")
                error_count += 1

    print(f"\nSummary for {target_repo.full_name}:")
    print(f"  Created: {created_count}")
    print(f"  Skipped (already exists): {skipped_count}")
    print(f"  Errors: {error_count}")

    return created_count, skipped_count, error_count


def main():
    """Main function to sync labels to all downstream repositories."""
    # Get GitHub token from environment
    github_token = os.environ.get("GITHUB_TOKEN")
    if not github_token:
        print("Error: GITHUB_TOKEN environment variable is not set")
        sys.exit(1)

    # Get the current repository from environment (set by GitHub Actions)
    current_repo_name = os.environ.get("GITHUB_REPOSITORY")
    if not current_repo_name:
        print("Error: GITHUB_REPOSITORY environment variable is not set")
        sys.exit(1)

    # Initialize GitHub client
    auth = Auth.Token(github_token)
    g = Github(auth=auth)

    # Get the source repository
    try:
        source_repo = g.get_repo(current_repo_name)
        org_name = source_repo.organization.login
        print(f"Source repository: {source_repo.full_name}")
        print(f"Organization: {org_name}")
    except GithubException as e:
        print(f"Error: Failed to access repository {current_repo_name}: {e}")
        sys.exit(1)

    # Load source labels
    print("\nFetching labels from source repository...")
    source_labels = get_labels(source_repo)
    print(f"Found {len(source_labels)} labels in source repository")

    # Load downstream repositories
    repos_file = Path("repos.yaml")
    if not repos_file.exists():
        print(f"Error: {repos_file} not found")
        sys.exit(1)

    downstream_repos = load_repos(repos_file)
    print(f"\nDownstream repositories to sync: {len(downstream_repos)}")
    for repo in downstream_repos:
        print(f"  - {repo}")

    # Sync labels to each downstream repository
    total_created = 0
    total_skipped = 0
    total_errors = 0

    for repo_name in downstream_repos:
        full_repo_name = f"{org_name}/{repo_name}"
        try:
            target_repo = g.get_repo(full_repo_name)
            created, skipped, errors = sync_labels_to_repo(source_labels, target_repo)
            total_created += created
            total_skipped += skipped
            total_errors += errors
        except GithubException as e:
            print(f"\n✗ Error: Failed to access repository {full_repo_name}: {e}")
            total_errors += 1

    # Print final summary
    print(f"\n{'=' * 60}")
    print("FINAL SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total labels created: {total_created}")
    print(f"Total labels skipped: {total_skipped}")
    print(f"Total errors: {total_errors}")
    print(f"{'=' * 60}")

    if total_errors > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
