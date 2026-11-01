#!/usr/bin/env bash
set -euo pipefail
branch="${1:?default branch required}"
# Never force-push or resolve conflicts automatically. Retry unrelated edits only.
for attempt in 1 2 3; do
    if git push origin "HEAD:refs/heads/$branch"; then
        exit 0
    fi
    if [ "$attempt" = 3 ]; then
        echo 'Public metadata push failed after bounded retries.' >&2
        exit 1
    fi
    git fetch origin "$branch"
    git rebase FETCH_HEAD
 done
