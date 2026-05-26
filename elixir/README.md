# Chug

Mix task for creating [Chug](https://github.com/crayment/chug) changelog entries.

Provides `mix chug.new` as a drop-in alternative to the `chug new` CLI command for Elixir projects — no Python tooling required.

## Installation

Add `chug` to your dependencies in `mix.exs`:

```elixir
def deps do
  [
    {:chug, "~> 0.1", only: :dev, runtime: false}
  ]
end
```

## Usage

```bash
mix chug.new --description "Fix session timeout" --category bug
mix chug.new --description "Add export endpoint" --category feature --stories sc-1234,sc-5678
```

Reads `chug.config.yml` from your project root. The `categories` key determines which values are valid.

For CI validation, changelog releases, and full documentation see the [Chug repository](https://github.com/crayment/chug).
