"""Command-line interface for EACopy."""

# Import built-in modules
import sys

# Import third-party modules
import click

# Import local modules
from . import __version__, copy, copy2, copytree, copy_with_server


@click.group()
@click.version_option(version=__version__)
def cli():
    """EACopy - High-performance file copy tool."""
    pass


@cli.command()
@click.argument("source", type=click.Path(exists=True, readable=True))
@click.argument("destination", type=click.Path(writable=True))
@click.option(
    "--preserve-metadata", "-p", is_flag=True, help="Preserve file metadata"
)
def cp(source, destination, preserve_metadata):
    """Copy a file from SOURCE to DESTINATION."""
    try:
        if preserve_metadata:
            copy2(source, destination)
        else:
            copy(source, destination)
        click.echo(f"Copied {source} to {destination}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("source", type=click.Path(exists=True, readable=True, file_okay=False, dir_okay=True))
@click.argument("destination", type=click.Path(writable=True))
@click.option("--symlinks", "-s", is_flag=True, help="Preserve symlinks")
@click.option("--ignore-dangling-symlinks", "-i", is_flag=True, help="Ignore dangling symlinks")
@click.option("--dirs-exist-ok", "-d", is_flag=True, help="Allow destination directory to exist")
def cptree(source, destination, symlinks, ignore_dangling_symlinks, dirs_exist_ok):
    """Copy a directory tree from SOURCE to DESTINATION."""
    try:
        copytree(
            source,
            destination,
            symlinks=symlinks,
            ignore_dangling_symlinks=ignore_dangling_symlinks,
            dirs_exist_ok=dirs_exist_ok,
        )
        click.echo(f"Copied directory tree from {source} to {destination}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("source", type=click.Path(exists=True, readable=True))
@click.argument("destination", type=click.Path(writable=True))
@click.argument("server_addr")
@click.option("--port", "-p", type=int, default=31337, help="EACopyService server port")
@click.option("--compression", "-c", type=int, default=0, help="Compression level (0-9)")
def server(source, destination, server_addr, port, compression):
    """Copy using EACopyService from SOURCE to DESTINATION via SERVER_ADDR."""
    try:
        copy_with_server(
            source,
            destination,
            server_addr,
            port=port,
            compression_level=compression,
        )
        click.echo(f"Copied {source} to {destination} using server {server_addr}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


def main():
    """Main entry point for the CLI."""
    return cli()
