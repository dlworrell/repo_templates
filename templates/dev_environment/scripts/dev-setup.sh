#!/usr/bin/env bash
# Check, and optionally fix, a Catalyst repository's local Git setup.
#
#   scripts/dev-setup.sh --check   report only (default)
#   scripts/dev-setup.sh --fix     also apply the safe local settings it reports
#
# Authority: Catylist ADR-0006 (signed commits, merge commits, no rewritten
# history), ADR-0007 (local checks are a convenience; CI is the gate) and the
# AEMS prompt prompts/git-workflow-dev-environment.md. This script changes only
# this clone's local Git configuration. It never prints, copies or creates a
# private key, never commits, and never pushes.
#
# Exit status: 0 when nothing needs attention, 1 when something does, 2 on
# misuse. Each line starts with ok, fixed, fixable or needs-you.
set -u

mode=check
case "${1:---check}" in
  --check) mode=check ;;
  --fix) mode=fix ;;
  -h|--help) sed -n '2,15p' "$0"; exit 0 ;;
  *) echo "usage: $0 [--check|--fix]" >&2; exit 2 ;;
esac

attention=0
say() { printf '%-9s %s\n' "$1" "$2"; }
needs() { say needs-you "$1"; attention=1; }

# fix_or_report DESCRIPTION KEY VALUE: set a local config value in --fix mode.
fix_or_report() {
  local description=$1 key=$2 value=$3
  if [ "$(git config --get "$key" 2>/dev/null)" = "$value" ]; then
    say ok "$description"
  elif [ "$mode" = fix ]; then
    git config --local "$key" "$value" && say fixed "$description"
  else
    say fixable "$description (run with --fix: git config $key '$value')"
    attention=1
  fi
}

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "not inside a Git work tree" >&2
  exit 2
fi
cd "$(git rev-parse --show-toplevel)" || exit 2

# 1. Git version: SSH commit signing needs Git 2.34 or newer.
version=$(git version | sed -E 's/^git version ([0-9]+)\.([0-9]+).*/\1 \2/')
read -r major minor <<<"$version"
if [ "${major:-0}" -gt 2 ] || { [ "${major:-0}" -eq 2 ] && [ "${minor:-0}" -ge 34 ]; }; then
  say ok "Git $(git version | awk '{print $3}')"
else
  needs "Git 2.34 or newer is needed for SSH commit signing"
fi

# 2. Identity.
for key in user.name user.email; do
  if [ -n "$(git config --get "$key" 2>/dev/null)" ]; then
    say ok "$key is set"
  else
    needs "$key is not set (git config --global $key '...'); use an address GitHub verifies for you"
  fi
done

# 3. Signing (Code, Law 3). The key itself is never printed.
signingkey=$(git config --get user.signingkey 2>/dev/null || true)
format=$(git config --get gpg.format 2>/dev/null || echo openpgp)
if [ -z "$signingkey" ]; then
  needs "no signing key (user.signingkey); add one and register it on GitHub as a Signing Key"
else
  if [ "$format" = ssh ]; then
    keyfile=${signingkey/#\~/$HOME}
    case "$signingkey" in
      key::*|ssh-*) say ok "SSH signing key configured inline" ;;
      *)
        if [ -f "$keyfile" ]; then
          pub=$keyfile
          case "$keyfile" in *.pub) ;; *) [ -f "$keyfile.pub" ] && pub="$keyfile.pub" ;; esac
          fingerprint=$(ssh-keygen -lf "$pub" 2>/dev/null | awk '{print $2}')
          say ok "SSH signing key configured${fingerprint:+ ($fingerprint)}"
        else
          needs "user.signingkey names a file that does not exist"
        fi ;;
    esac
  else
    say ok "OpenPGP signing key configured"
  fi
  fix_or_report "commits are signed" commit.gpgsign true
  fix_or_report "tags are signed" tag.gpgsign true
fi

# 4. Remote and tracking.
if git remote get-url origin >/dev/null 2>&1; then
  say ok "origin is $(git remote get-url origin | sed -E 's#://[^@/]+@#://#')"
  wanted='+refs/heads/*:refs/remotes/origin/*'
  current=$(git config --local --get-all remote.origin.fetch 2>/dev/null || true)
  if printf '%s\n' "$current" | grep -qxF "$wanted"; then
    say ok "origin fetches every branch"
  elif [ "$mode" = fix ]; then
    git config --local --add remote.origin.fetch "$wanted" && say fixed "origin fetches every branch"
  else
    say fixable "origin fetches only some branches; new branches will not track (run with --fix)"
    attention=1
  fi
else
  needs "no origin remote"
fi

branch=$(git symbolic-ref --quiet --short HEAD 2>/dev/null || true)
default=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null | sed 's#^origin/##')
default=${default:-main}
# A working branch tracks its own remote branch, never a shared one: the
# default branch or the Catylist ADR-0013 dev-daily and fitment branches.
case " $default dev-daily fitment " in
  *" $branch "*) shared_branch=1 ;;
  *) shared_branch=0 ;;
esac
if [ -n "$branch" ] && [ "$shared_branch" = 0 ]; then
  upstream=$(git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null || true)
  for shared in "$default" dev-daily fitment; do
    if [ "$upstream" = "origin/$shared" ]; then
      needs "$branch tracks origin/$shared; push it with 'git push -u origin $branch' so it tracks its own branch"
    fi
  done
fi

# 5. Merge-based workflow: never rebase pushed work.
fix_or_report "git pull merges instead of rebasing" pull.rebase false

# 6. Commit message template with the ADR line.
if [ -f .gitmessage ]; then
  fix_or_report "commit message template" commit.template .gitmessage
fi

exit "$attention"
