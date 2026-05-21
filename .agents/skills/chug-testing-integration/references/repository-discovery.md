# Repository Discovery

Resolve local clone paths before running any scenario.

The public repositories are fixed:

- product repo: `crayment/chug`
- consumer repo: `crayment/chug-testing`

The local clone paths are not fixed and must be discovered.

## Required Outputs

Resolve these two logical paths before continuing:

- `PRODUCT_REPO_DIR`
- `CONSUMER_REPO_DIR`

All scenario steps should use those logical names, not hardcoded local paths.

## Resolution Order

Resolve each repo in this order.

### 1. Reuse the current working repo when it already matches

Run:

```bash
git remote get-url origin
```

If the current repo's `origin` matches one of these, use the current directory:

- `git@github.com:crayment/chug.git`
- `https://github.com/crayment/chug.git`
- `git@github.com:crayment/chug-testing.git`
- `https://github.com/crayment/chug-testing.git`

### 2. Reuse an existing local clone when one is already available

Check likely workspace locations first. Prefer explicit candidate directories over a wide filesystem search.

Good starting points:

- the parent directory of the current repo
- `~/dev`
- any obvious project workspace root already in use on this machine

For each candidate directory, verify it by checking the git remote:

```bash
git -C "/path/to/candidate" remote get-url origin
```

Only trust the remote URL, not the directory name.

### 3. Clone when no usable local repo exists

If no matching local clone exists, clone the repo into a predictable location.

Recommended default:

```bash
mkdir -p "$HOME/dev"
git clone git@github.com:crayment/chug.git "$HOME/dev/chug"
git clone git@github.com:crayment/chug-testing.git "$HOME/dev/chug-testing"
```

If `$HOME/dev` is clearly not the user's normal workspace root, pick a nearby workspace directory instead and record the actual path used.

### 4. Ask once if multiple valid clones exist

If more than one valid clone exists for the same repo, prefer:

1. the cleanest working tree
2. the clone nearest the current workspace
3. the most recently updated clone

If the choice is still ambiguous, ask for confirmation.

## Cleanliness Check

Before using a clone for a scenario, inspect its working tree:

```bash
git -C "$PRODUCT_REPO_DIR" status --short
git -C "$CONSUMER_REPO_DIR" status --short
```

If a scenario needs isolation and the repo is dirty, create a fresh clone instead of mutating an uncertain local state.

## Recording

At the start of each scenario report, record the resolved paths:

- `PRODUCT_REPO_DIR=<resolved path>`
- `CONSUMER_REPO_DIR=<resolved path>`
