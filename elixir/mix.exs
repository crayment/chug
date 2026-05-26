# ABOUTME: Mix project definition for the Chug Elixir package.
# ABOUTME: Publishes the `mix chug.new` task to Hex.pm.

defmodule Chug.MixProject do
  use Mix.Project

  @version "0.1.3"
  @source_url "https://github.com/crayment/chug"

  def project do
    [
      app: :chug,
      version: @version,
      elixir: "~> 1.19",
      description: description(),
      package: package(),
      deps: deps(),
      docs: docs(),
      name: "Chug",
      source_url: @source_url
    ]
  end

  def application do
    [extra_applications: [:logger]]
  end

  defp description do
    "Mix task for creating Chug changelog entries. Provides `mix chug.new` as a " <>
      "drop-in alternative to the Chug CLI for Elixir projects."
  end

  defp package do
    [
      licenses: ["MIT"],
      links: %{"GitHub" => @source_url},
      files: ~w(lib mix.exs README.md LICENSE)
    ]
  end

  defp deps do
    [
      {:yaml_elixir, "~> 2.9"},
      {:ymlr, "~> 5.0"},
      {:ex_doc, "~> 0.34", only: :dev, runtime: false}
    ]
  end

  defp docs do
    [
      main: "Mix.Tasks.Chug.New",
      source_url: @source_url
    ]
  end
end
