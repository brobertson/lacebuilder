#!/usr/bin/env python

"""Tests for `lacebuilder` package."""

import pytest

from click.testing import CliRunner

from lacebuilder import lacebuilder
from lacebuilder import cli
from lacebuilder import greek_tools


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    #assert 'lacebuilder.cli.main' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert 'packimages' in help_result.output

def test_greek_tools_identify_greek_chars():
    assert greek_tools.is_greek_char('β')
    assert greek_tools.is_greek_char('ῇ')

def test_greek_tools_identify_greek_string():
    assert greek_tools.is_greek_string('μαχ(οῦμαι)')

def test_greek_tools_preprocess_words():
    assert greek_tools.preprocess_word('δ\'') == 'δ’'

def test_greek_tools_strip_accents():
    assert greek_tools.strip_accents('ἐχθρῶν') == 'εχθρων'
