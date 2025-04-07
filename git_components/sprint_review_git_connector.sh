#!/bin/bash

# ===== Default values =====
days=1
repo_path=""
start_date=""
end_date=""

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
    --start-date)
      start_date="$2"
      shift 2
      ;;
    --end-date)
      end_date="$2"
      shift 2
      ;;
    *)
      echo "❌ Unknown option: $1"
      echo "Usage: ./generator_git_logs_for.sh --path /path/to/repo [--days N] [--start-date YYYY-MM-DD --end-date YYYY-MM-DD]"
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

# ===== Get Git author and repo name =====
author_name="$(git config user.name)"
repo_name=$(basename "$(git rev-parse --show-toplevel)")

# ===== Print project/repo name =====
echo "=== Project: $repo_name ==="

# ===== Scan branches and print logs =====
for branch in $(git for-each-ref --format='%(refname:short)' refs/heads/); do
  if [[ -n "$start_date" && -n "$end_date" ]]; then
    date_range="--since=$start_date --until=$end_date"
  else
    date_range="--since=${days} days ago"
  fi

  logs=$(git log "$branch" $date_range --author="$author_name" \
         --pretty=format:"%ad %h %s" --date=short)

  if [[ -n "$logs" ]]; then
    echo "===== Branch: $branch ====="
    echo "$logs"
    echo ""
  fi
done