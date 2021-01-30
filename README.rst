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

* Generates a base image package for all derived OCR runs, binarizing all images
* Generates OCR output packages with the enhanced data used to make editing OCR easy in Lace, including word spellcheck status and dehyphenation
* Automatically corrects the word bounding boxes of kraken hOCR output

Examples
~~~~~~~~
lacebuilder offers two subcommands, ``packimages`` and ``packtexts``. These have their own parameters. The parameters ``--outputdir`` and ``--metadatafile`` are common to both of the subcommands, so they are set before them. At present, you cannot chain the subcommands. To access the ``--help`` for the subcommands, you must properly set these output parameters, thus::

    lacebuilder --outputdir /tmp/ --metadatafile /tmp/myfile_meta.xml packtexts --help

Building an image package::

    lacebuilder --outputdir /home/brucerob/ --metadatafile ~/Test_Lacebuilder/552464779_meta.xml packimages  --imagedir ~/Test_Tarantella/test outputdir: /home/brucerob/
    generating image xar archive
    Binarizing and compressing images
    image archive of 111 images saved to /home/brucerob/552464779_images.xar
    
More information is required to build an hOCR output text package because Lace uses it to store multiple OCR 'runs' of a given image set and eventually to search and compile runs that have been completed using the same classifier::

    lacebuilder --outputdir /home/brucerob/ --metadatafile ~/Test_Tarantella/552464779_meta.xml packtexts  --hocrdir ~/Test_Tarantella/test_hocr_out/ --classifier ~/Downloads/Kraken-Greek-Classifiers-and-Samples/porson_2020-10-10-11-54-25_best.mlmodel --imagexarfile ~/552464779_images.xar
    dehyphenating
    spellchecking
    generating hocr xar
    accuracy 91%, Greek acc. 91%; completed 00%, Greek completed 00%
    total:  20669 ; total correct: 11369
    writing this data to  /tmp/tmpo0_6nin6total.xml
    text archive from date 2021-01-30-16-05-42 saved to /home/brucerob/552464779-2021-01-30-16-05-42-porson_2020-10-10-11-54-25_best-texts.xar


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
