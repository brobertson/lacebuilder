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




Lacebuilder is a friendly command-line application that generates packages for the `Lace <https://github.com/brobertson/Lace2>`_ in-browser OCR to TEI web editing application. Point it to an image directory and corresponding hOCR output directory, as well as to a simple xml metadata file, and it produces the .xar packages that can be installed in Lace through eXist-db's drag-and-drop package manager.


* Free software: BSD license
* Documentation: https://lacebuilder.readthedocs.io.


Features
--------

* Gemerates a base image package for all derived OCR runs, binarizing all images
* Generates OCR output packages with the enhanced data used to make editing OCR easy in Lace, including word spellcheck status and dehyphenation
* Automatically corrects the word bounding boxes of kraken hOCR output

Examples
~~~~~~~~

Building an image package:

::

    lacebuilder --outputdir /home/brucerob/ --metadatafile ~/Test_Lacebuilder/552464779_meta.xml packimages  --imagedir ~/Test_Tarantella/test outputdir: /home/brucerob/
    generating image xar archive
    Binarizing and compressing images
    image archive of 111 images saved to /home/brucerob/552464779_images.xar"
    
Building an hOCR output text package:




Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
