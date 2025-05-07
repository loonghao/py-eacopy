"""Test CLI functionality."""

# Import built-in modules
import sys
from unittest import mock
from click.testing import CliRunner

# Import local modules
from eacopy import cli


def test_cli_version():
    """Test CLI version command."""
    runner = CliRunner()
    result = runner.invoke(cli.cli, ["--version"])
    assert result.exit_code == 0
    assert "version" in result.output.lower()


@mock.patch("eacopy.cli.copy")
def test_cli_cp(mock_copy):
    """Test CLI cp command."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create a test file
        with open("source.txt", "w") as f:
            f.write("test content")

        result = runner.invoke(cli.cli, ["cp", "source.txt", "dest.txt"])
        assert result.exit_code == 0
        mock_copy.assert_called_once_with("source.txt", "dest.txt")
        assert "Copied" in result.output


@mock.patch("eacopy.cli.copy2")
def test_cli_cp_with_metadata(mock_copy2):
    """Test CLI cp command with preserve metadata."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create a test file
        with open("source.txt", "w") as f:
            f.write("test content")

        result = runner.invoke(cli.cli, ["cp", "source.txt", "dest.txt", "--preserve-metadata"])
        assert result.exit_code == 0
        mock_copy2.assert_called_once_with("source.txt", "dest.txt")
        assert "Copied" in result.output


@mock.patch("eacopy.cli.copytree")
def test_cli_cptree(mock_copytree):
    """Test CLI cptree command."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create a test directory
        import os
        os.makedirs("source_dir")

        result = runner.invoke(cli.cli, ["cptree", "source_dir", "dest_dir"])
        assert result.exit_code == 0
        mock_copytree.assert_called_once_with(
            "source_dir",
            "dest_dir",
            symlinks=False,
            ignore_dangling_symlinks=False,
            dirs_exist_ok=False,
        )
        assert "Copied directory tree" in result.output


@mock.patch("eacopy.cli.copy_with_server")
def test_cli_server(mock_copy_with_server):
    """Test CLI server command."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create a test file
        with open("source.txt", "w") as f:
            f.write("test content")

        result = runner.invoke(cli.cli, ["server", "source.txt", "dest.txt", "server.example.com"])
        assert result.exit_code == 0
        mock_copy_with_server.assert_called_once_with(
            "source.txt",
            "dest.txt",
            "server.example.com",
            port=31337,
            compression_level=0,
        )
        assert "Copied" in result.output


@mock.patch("eacopy.cli.copy")
def test_cli_error(mock_copy):
    """Test CLI error handling."""
    mock_copy.side_effect = Exception("Test error")
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create a test file
        with open("source.txt", "w") as f:
            f.write("test content")

        result = runner.invoke(cli.cli, ["cp", "source.txt", "dest.txt"])
        assert result.exit_code == 1
        assert "Error" in result.output
