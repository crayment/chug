# ABOUTME: Mix task implementing `mix chug.new` for creating changelog entry files.
# ABOUTME: Reads chug.config.yml from the project root and writes a timestamped YAML file to changes/.

defmodule Mix.Tasks.Chug.New do
  @shortdoc "Create a new Chug changelog entry"

  @moduledoc """
  Creates a new pending changelog entry in the `changes/` directory.

  ## Usage

      mix chug.new --description "Fix session timeout" --category bug
      mix chug.new --description "Add export endpoint" --category feature --stories sc-1234,sc-5678

  ## Options

    * `--description` - (required) User-facing description of the change
    * `--category` - (required) Category for the change; must be one configured in `chug.config.yml`
    * `--stories` - (optional) Comma-separated story/ticket references

  ## Configuration

  Reads `chug.config.yml` from the current working directory. The `categories` key
  determines which category values are valid.
  """

  use Mix.Task

  @config_file "chug.config.yml"
  @changes_dir "changes"

  @impl Mix.Task
  def run(args) do
    {opts, _, _} =
      OptionParser.parse(args,
        strict: [description: :string, category: :string, stories: :string]
      )

    description = Keyword.get(opts, :description) || error_exit("--description is required")
    category = Keyword.get(opts, :category) || error_exit("--category is required")
    stories = parse_stories(Keyword.get(opts, :stories))

    config = load_config()
    valid_categories = Map.get(config, "categories", [])

    unless category in valid_categories do
      error_exit(
        "Category '#{category}' is not in chug.config.yml. Valid categories: #{Enum.join(valid_categories, ", ")}"
      )
    end

    File.mkdir_p!(@changes_dir)

    path = Path.join(@changes_dir, filename_for(description))
    content = build_entry(description, category, stories)
    File.write!(path, content)

    Mix.shell().info("Created changelog entry: #{path}")
  end

  defp load_config do
    unless File.exists?(@config_file) do
      error_exit("#{@config_file} not found. Run `chug init` to set up Chug in this repository.")
    end

    Application.ensure_all_started(:yaml_elixir)

    case YamlElixir.read_from_file(@config_file) do
      {:ok, config} -> config
      {:error, reason} -> error_exit("Failed to read #{@config_file}: #{inspect(reason)}")
    end
  end

  defp parse_stories(nil), do: []

  defp parse_stories(stories_str) do
    stories_str
    |> String.split(",")
    |> Enum.map(&String.trim/1)
    |> Enum.reject(&(&1 == ""))
  end

  defp filename_for(description) do
    timestamp = DateTime.utc_now() |> Calendar.strftime("%Y-%m-%dT%H%M%S")
    slug = description |> String.downcase() |> String.replace(~r/[^a-z0-9]+/, "-") |> String.trim("-")
    slug = if slug == "", do: "change", else: slug
    "#{timestamp}-#{slug}.yml"
  end

  defp build_entry(description, category, stories) do
    authors = detect_authors()

    lines = [
      "description: #{yaml_string(description)}",
      "category: #{yaml_string(category)}"
    ]

    lines =
      if stories != [] do
        stories_yaml = Enum.map_join(stories, "", &"- #{&1}\n")
        lines ++ ["stories:\n#{indent(stories_yaml)}"]
      else
        lines
      end

    Enum.join(lines, "\n") <> "\n" <> authors_yaml(authors)
  end

  defp detect_authors do
    name = git_config("user.name")
    github = git_config("github.user")

    if name == nil and github == nil do
      []
    else
      author =
        [name && {"name", name}, github && {"github", github}]
        |> Enum.reject(&is_nil/1)
        |> Map.new()

      [author]
    end
  end

  defp git_config(key) do
    case System.cmd("git", ["config", key], stderr_to_stdout: false) do
      {value, 0} ->
        value = String.trim(value)
        if value == "", do: nil, else: value

      _ ->
        nil
    end
  end

  defp authors_yaml([]), do: "authors: []\n"

  defp authors_yaml(authors) do
    entries =
      Enum.map_join(authors, "", fn author ->
        first_line =
          cond do
            author["name"] -> "- name: #{yaml_string(author["name"])}"
            author["github"] -> "- github: #{yaml_string(author["github"])}"
          end

        extra_lines =
          [author["github"] && author["name"] && "  github: #{yaml_string(author["github"])}"]
          |> Enum.reject(&is_nil/1)

        ([first_line] ++ extra_lines ++ [""])
        |> Enum.join("\n")
      end)

    "authors:\n#{entries}"
  end

  defp yaml_string(value) do
    escaped = String.replace(value, "\"", "\\\"")
    "\"#{escaped}\""
  end

  defp indent(str) do
    str
    |> String.split("\n")
    |> Enum.map_join("\n", fn
      "" -> ""
      line -> "  " <> line
    end)
  end

  defp error_exit(message) do
    Mix.raise(message)
  end
end
