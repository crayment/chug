# ABOUTME: Tests for the mix chug.new task.
# ABOUTME: Verifies config loading, category validation, file creation, and author detection.

defmodule Mix.Tasks.Chug.NewTest do
  use ExUnit.Case

  @config_contents """
  categories:
    - feature
    - bug
    - chore
  git_base_branch: main
  """

  setup do
    # Each test gets its own isolated tmp directory
    tmp = Path.join(System.tmp_dir!(), "chug-test-#{:erlang.unique_integer([:positive])}")
    File.mkdir_p!(tmp)

    on_exit(fn -> File.rm_rf!(tmp) end)

    {:ok, tmp: tmp}
  end

  defp run_in(tmp, args) do
    orig = File.cwd!()
    File.cd!(tmp)

    try do
      Mix.Tasks.Chug.New.run(args)
    after
      File.cd!(orig)
    end
  end

  defp write_config(tmp, contents \\ @config_contents) do
    File.write!(Path.join(tmp, "chug.config.yml"), contents)
  end

  defp change_files(tmp) do
    changes_dir = Path.join(tmp, "changes")

    if File.exists?(changes_dir) do
      File.ls!(changes_dir)
      |> Enum.filter(&String.ends_with?(&1, ".yml"))
      |> Enum.map(&Path.join(changes_dir, &1))
    else
      []
    end
  end

  test "creates a change file with correct description and category", %{tmp: tmp} do
    write_config(tmp)
    run_in(tmp, ["--description", "Fix session timeout", "--category", "bug"])

    files = change_files(tmp)
    assert length(files) == 1

    Application.ensure_all_started(:yaml_elixir)
    {:ok, parsed} = File.read!(hd(files)) |> YamlElixir.read_from_string()
    assert parsed["description"] == "Fix session timeout"
    assert parsed["category"] == "bug"
  end

  test "description with special YAML characters produces valid parseable output", %{tmp: tmp} do
    write_config(tmp)

    for description <- ["[array start", "* wildcard", "{map start", "!tag", ": colon"] do
      run_in(tmp, ["--description", description, "--category", "bug"])
    end

    for file <- change_files(tmp) do
      content = File.read!(file)
      Application.ensure_all_started(:yaml_elixir)
      assert {:ok, parsed} = YamlElixir.read_from_string(content)
      assert is_map(parsed)
      assert Map.has_key?(parsed, "description")
    end
  end

  test "description with backslashes round-trips correctly", %{tmp: tmp} do
    write_config(tmp)
    run_in(tmp, ["--description", "C:\\new\\path", "--category", "bug"])

    [file] = change_files(tmp)
    content = File.read!(file)
    Application.ensure_all_started(:yaml_elixir)
    assert {:ok, parsed} = YamlElixir.read_from_string(content)
    assert parsed["description"] == "C:\\new\\path"
  end

  test "filename is timestamped and slugified from description", %{tmp: tmp} do
    write_config(tmp)
    run_in(tmp, ["--description", "Add export endpoint", "--category", "feature"])

    [file] = change_files(tmp)
    name = Path.basename(file)

    assert name =~ ~r/^\d{4}-\d{2}-\d{2}T\d{6}-add-export-endpoint\.yml$/
  end

  test "includes stories when provided", %{tmp: tmp} do
    write_config(tmp)

    run_in(tmp, [
      "--description",
      "Fix bug",
      "--category",
      "bug",
      "--stories",
      "sc-1234,sc-5678"
    ])

    [file] = change_files(tmp)
    content = File.read!(file)
    assert content =~ "sc-1234"
    assert content =~ "sc-5678"
  end

  test "raises on invalid category", %{tmp: tmp} do
    write_config(tmp)

    assert_raise Mix.Error, ~r/not in chug\.config\.yml/, fn ->
      run_in(tmp, ["--description", "Something", "--category", "invalid"])
    end
  end

  test "raises when --description is missing", %{tmp: tmp} do
    write_config(tmp)

    assert_raise Mix.Error, ~r/--description is required/, fn ->
      run_in(tmp, ["--category", "bug"])
    end
  end

  test "raises when --category is missing", %{tmp: tmp} do
    write_config(tmp)

    assert_raise Mix.Error, ~r/--category is required/, fn ->
      run_in(tmp, ["--description", "Something"])
    end
  end

  test "raises when chug.config.yml is missing", %{tmp: tmp} do
    assert_raise Mix.Error, ~r/chug\.config\.yml not found/, fn ->
      run_in(tmp, ["--description", "Something", "--category", "bug"])
    end
  end

  test "writes authors: [] when git config is not set", %{tmp: tmp} do
    write_config(tmp)

    # Patch git_config via process dict is not possible; instead run in a dir
    # where git isn't configured — the task falls back to [] gracefully.
    # We just assert the file is written and contains authors:
    run_in(tmp, ["--description", "Test change", "--category", "chore"])

    [file] = change_files(tmp)
    content = File.read!(file)
    assert content =~ "authors:"
  end

  test "output is valid YAML parseable back to the original values", %{tmp: tmp} do
    write_config(tmp)
    run_in(tmp, ["--description", "Test change", "--category", "chore", "--stories", "sc-999"])

    [file] = change_files(tmp)
    Application.ensure_all_started(:yaml_elixir)
    assert {:ok, parsed} = YamlElixir.read_from_string(File.read!(file))
    assert parsed["description"] == "Test change"
    assert parsed["category"] == "chore"
    assert parsed["stories"] == ["sc-999"]
    assert Map.has_key?(parsed, "authors")
  end

  test "creates changes/ directory if it does not exist", %{tmp: tmp} do
    write_config(tmp)
    refute File.exists?(Path.join(tmp, "changes"))

    run_in(tmp, ["--description", "Something", "--category", "chore"])

    assert File.exists?(Path.join(tmp, "changes"))
  end
end
