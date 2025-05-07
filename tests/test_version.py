"""Test version information."""

# Import local modules
import eacopy


def test_version():
    """Test that version is a string."""
    assert isinstance(eacopy.__version__, str)
    assert eacopy.__version__ != ""


def test_eacopy_version():
    """Test that EACopy version is a string."""
    assert isinstance(eacopy.__eacopy_version__, str)
    assert eacopy.__eacopy_version__ != ""
