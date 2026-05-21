# Scenario: CLI Happy Path

Validate the Chug CLI in the consumer repository without relying on GitHub Actions.

## Goal

Prove that a team can use Chug locally in a normal repository from init through release.

## Steps

1. Resolve `PRODUCT_REPO_DIR` and `CONSUMER_REPO_DIR` using `repository-discovery.md`
2. Work in `CONSUMER_REPO_DIR`
3. Ensure `main` is clean before starting
4. Install the current local product build:

```bash
uv tool install --force --refresh "$PRODUCT_REPO_DIR"
```

5. Run:

```bash
chug init
chug new --description "CLI scenario change" --category chore --stories sc-10001
chug preview
chug release --version 0.9.0-cli-test
```

6. Inspect `CHANGELOG.md`
7. Verify `changes/` no longer contains the processed file

## Expected Result

- all commands exit successfully
- preview contains the pending change
- release writes a new version section
- the processed change file is deleted

## Record

- `PRODUCT_REPO_DIR`
- `CONSUMER_REPO_DIR`
- resulting `CHANGELOG.md` diff
- release command output
- any formatting surprises
