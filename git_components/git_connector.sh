#!/bin/bash

# ===== Default values =====
days=1
repo_path=""

# ===== Parse CLI arguments =====
while [[ $# -gt 0 ]]; do
  case $1 in
    --days)
      days="$2"
      shift 2
      ;;
    --path)
      repo_path="$2"
      shift 2
      ;;
    *)
      echo "❌ Unknown option: $1"
      echo "Usage: ./generator_git_logs_for.sh --path /path/to/repo [--days N]"
      exit 1
      ;;
  esac
done

# ===== Validate inputs =====
if [[ -z "$repo_path" ]]; then
  echo "❌ Please provide a repo path using --path"
  exit 1
fi

# ===== Change to repo directory =====
cd "$repo_path" || { echo "❌ Failed to access repo at $repo_path"; exit 1; }

# ===== Get Git author =====
author_name="$(git config user.name)"

# ===== Scan branches and print logs =====
for branch in $(git for-each-ref --format='%(refname:short)' refs/heads/); do
  logs=$(git log "$branch" --since="${days} days ago" --author="$author_name" \
         --pretty=format:"%ad %h %s" --date=short)

  if [[ -n "$logs" ]]; then
    echo "===== Branch: $branch ====="
    echo "$logs"
    echo ""
  fi
done