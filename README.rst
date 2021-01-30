===========
Lacebuilder
===========


.. image:: https://img.shields.io/pypi/v/lacebuilder.svg
        :target: https://pypi.python.org/pypi/lacebuilder

.. image:: https://img.shields.io/travis/brobertson/lacebuilder.svg
        :target: https://travis-ci.com/brobertson/lacebuilder

.. image:: https://readthedocs.org/projects/lacebuilder/badge/?version=latest
        :target: https://lacebuilder.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




Lacebuilder is a friendly command-line application that generates packages for the [Lace](https://github.com/brobertson/Lace2) in-browser OCR to TEI web editing application. You point it to your image directory and your hOCR output directory, as well as to a simple xml metadata file, and it produces the .xar packages that can be installed in Lace through eXist-db's drag-and-drop package manager.


* Free software: BSD license
* Documentation: https://lacebuilder.readthedocs.io.


Features
--------

* Gemerates a base image package for all derived OCR runs
* Generates OCR output packages with the enhanced data used to make editing OCR easy in Lace, including word spellcheck status and dehyphenation
* Automatically corrects the word bounding boxes of kraken hOCR output

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
