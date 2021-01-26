"""Main module."""
from . import (
    accuracySvgAndTotals,
    assess_hocr_dir,
    fix_kraken_hocr,
    dehyphenate,
    generate_spellcheck_file,
    spellcheck_hocr,
)


def generate_image_xar(image_dir, output_dir, metadata_file, verbose, clobber):
    import glob, os, shutil, tempfile
    from halo import Halo
    from os.path import basename
    from pathlib import Path
    from zipfile import ZipFile

    # test if output file exists. If it does and clobber is False, then exit without doing the following
    print("generating image xar archive")

    identifier = get_identifier_from_metadata_file(metadata_file)
    if verbose:
        print("identifier: ", identifier)
    temp_dir = tempfile.mkdtemp()
    output_zip_file_path = os.path.join(output_dir, identifier + "_images.xar")
    if os.path.exists(output_zip_file_path) and not (clobber == True):
        print(
            "Output xar file '",
            output_zip_file_path,
            "' exists, and you have not set --clobber, so exiting.",
        )
        return 0
    if verbose:
        print("using as tempdir: '", temp_dir, "'")

    # collect and sort all the image files in the inputdir
    types = ["*.tif", "*.png", "*.jpg", "*.tiff"]
    if verbose:
        print("output dir for all images: ", output_dir)
    all_image_files = []
    for a_type in types:
        this_type_files = glob.glob(os.path.join(image_dir, a_type))
        all_image_files += this_type_files
    all_image_files.sort()
    if verbose:
        print("Input image files:")
        print(all_image_files)

    # binarize all the images and save in a temp dir
    spinner = Halo(text="Binarizing and compressing images", spinner="dots")
    spinner.start()
    output_counter = 1
    for input_image_file in all_image_files:
        fileout_name = identifier + "_" + str(output_counter).zfill(4) + ".png"
        if verbose:
            print("fileout name: ", fileout_name)
        fileout_path = os.path.join(temp_dir, fileout_name)
        binarize_skimage(input_image_file, fileout_path, verbose)
        output_counter = output_counter + 1
    spinner.stop()
    # save the xslt-generated metadata files to the temp dir
    with open(os.path.join(temp_dir, "expath-pkg.xml"), "w") as f:
        f.write(generate_image_expath(identifier))
    with open(os.path.join(temp_dir, "meta.xml"), "wb") as f:
        image_metadata = generate_image_meta(metadata_file)
        # I thought it would be fun to pass this to the hocr-generating command,
        # but chaining commands like this in Click looks daunting for a first try
        f.write(image_metadata)
    with open(os.path.join(temp_dir, "repo.xml"), "wb") as f:
        f.write(generate_image_repo(metadata_file))

    # save static metadata files to the temp dir
    static_files_dir = Path(__file__).parent / "static_for_image_xar"
    static_files = os.listdir(static_files_dir)
    for file_name in static_files:
        shutil.copy(os.path.join(static_files_dir, file_name), temp_dir)

    # generate the zip file and save to outputdir
    with ZipFile(output_zip_file_path, "w") as zipObj:
        for filename in os.listdir(temp_dir):
            filePath = os.path.join(temp_dir, filename)
            zipObj.write(filePath, basename(filePath))
    print("image archive of", output_counter, "images saved to", output_zip_file_path)


def get_identifier_from_metadata_file(metadata_file):
    import lxml.etree as ET

    tree = ET.parse(metadata_file)
    return tree.xpath("/metadata/identifier")[0].text


def generate_hocr_xar(
    hocr_dir,
    output_dir,
    metadata_file,
    imagexarfile,
    dictionary_file,
    ocr_engine,
    classifier,
    datetime,
    verbose,
    clobber,
):
    import glob, os, shutil, tempfile
    import lxml.etree as etree
    import datetime as dt
    import lxml.etree as ET
    from halo import Halo
    from os.path import basename
    from pathlib import Path
    import traceback
    from zipfile import ZipFile

    print("generating hocr xar")
    # set the datetime if it isn't given
    if datetime == None:
        now = dt.datetime.now()
        datetime = now.strftime("%Y-%m-%d-%H-%M-%S")
        if verbose:
            print("supplying datetime for this OCR run:", datetime)
    identifier = ""
    repo_file_string = ""

    #change classifier variable to be the name of the classifier, not path to the actual file
    classifier = Path(classifier).stem

    if not (metadata_file == None):
        identifier = get_identifier_from_metadata_file(metadata_file.name)
        xsl_file = Path(__file__).parent / "XSLT/make_repo_texts.xsl"
        xsl_file_handle = open(xsl_file, "r")
        xslt = ET.parse(xsl_file_handle)
        dom = ET.parse(open(metadata_file.name, "r"))
        transform = ET.XSLT(xslt)
        newdom = transform( dom, identifier=etree.XSLT.strparam(identifier), classifier=etree.XSLT.strparam(classifier), rundate=etree.XSLT.strparam(datetime))
        repo_file_string = ET.tostring(newdom)

    if not (imagexarfile == None):
        try:
            print("archive is:", imagexarfile)
            archive = ZipFile(imagexarfile.name, "r")
            metadata = archive.read("meta.xml")
            root = ET.fromstring(metadata)
            identifier = get_dc_element_from_metadata("identifier", root)
            if verbose:
                print("Using identifier from image xar file:", identifier)
            repo_file_string = make_text_repo_string(root, datetime)

        except Exception as e:
            print("Failed to open image archive at", metadata_file, "Exiting ...")
            print(e)
            exit(0)

    # get the final file name and check if we're clobbering
    output_file_name = identifier + "-" + datetime + "-" + classifier + "-texts.xar"
    output_file_path = os.path.join(output_dir, output_file_name)
    if os.path.exists(output_file_path) and not (clobber):
        print(
            "the output file",
            output_file_path,
            "already exists, and you've set '--clobber' to false, so I'm exiting without doing anything.",
        )
        exit(0)
    # collect and sort all the hocr files in the inputdir
    types = ["*.hocr", "*.html", "*.xhtml", "*.htm"]
    all_hocr_files = []
    for a_type in types:
        this_type_files = glob.glob(os.path.join(hocr_dir, a_type))
        all_hocr_files += this_type_files
    all_hocr_files.sort()
    if verbose:
        print("Input hocr files:")
        print(all_hocr_files)
    xhtml_temp_dir = tempfile.mkdtemp()
    output_counter = 1
    for hocr_file in all_hocr_files:
        fileout_name = identifier + "_" + str(output_counter).zfill(4) + ".html"
        # if verbose:
        #    print("fileout name: ", fileout_name)
        fileout_path = os.path.join(xhtml_temp_dir, fileout_name)
        shutil.copyfile(hocr_file, fileout_path)
        output_counter = output_counter + 1
    xslt_to_xhtml = etree.XML(
        """\
    <xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
       xmlns:html='http://www.w3.org/1999/xhtml'>

       <xsl:template match="*">
        <xsl:element name="html:{local-name(.)}">
          <xsl:apply-templates select="@*|*|text()"/>
           </xsl:element>
           </xsl:template>

           <xsl:template match="@*">
             <xsl:attribute name="{name(.)}"><xsl:value-of
             select="."/></xsl:attribute>
             </xsl:template>

             </xsl:stylesheet>"""
    )
    transform_to_xhtml = etree.XSLT(xslt_to_xhtml)
    xhtml_dehyph_temp_dir = tempfile.mkdtemp()
    if verbose:
        print("dehyphenation temp dir:", xhtml_dehyph_temp_dir)
    spinner = Halo(text="dehyphenating", spinner="dots")
    spinner.start()
    all_renamed_hocr_files = os.listdir(xhtml_temp_dir)
    for file_name in all_renamed_hocr_files:
        file_path = os.path.join(xhtml_temp_dir, file_name)
        with open(file_path) as file_path:
            try:
                tree = etree.parse(file_path)
                xhtml = transform_to_xhtml(tree)
                if ocr_engine == "kraken":
                    fix_kraken_hocr.get_word_span_area(xhtml, verbose)
                    fix_kraken_hocr.clean_ocr_page_title(xhtml, file_name)
                    try:
                        fix_kraken_hocr.share_space_spans(xhtml, verbose)
                    except Exception:
                        print(traceback.format_exc())
                        exit()
                    fix_kraken_hocr.confidence_summary(xhtml)
                dehyphenate.convert_ocrx_to_ocr(xhtml)
                dehyphenate.remove_meta_tags(xhtml)
                dehyphenate.identify(xhtml)
                dehyphenate.dehyphenate(xhtml, file_name, verbose)
                dehyphenate.add_dublin_core_tags(xhtml)
                out_path = os.path.join(xhtml_dehyph_temp_dir, file_name)
                xhtml.write(
                    out_path, pretty_print=True, xml_declaration=True, encoding="utf-8"
                )
            except Exception as e:
                print("This exception was thrown on file {}".format(file_name))
                print(e)
    spinner.stop()
    # now generate a spellcheck file
    spinner = Halo(text="spellchecking", spinner="dots")
    spinner.start()
    no_accent_dict_file_path = (
        Path(__file__).parent / "Dictionaries/unique_no_accent_list.csv"
    )
    # TODO: Parameterize this, so we can set the dictionary on the command line
    dictionary_file_path = (
        Path(__file__).parent / "Dictionaries/english_greek_latin.txt"
    )
    spellcheck_file_path = tempfile.mktemp()
    if verbose:
        print("spellcheck file is:", spellcheck_file_path)
    generate_spellcheck_file.make_spellcheck_file(
        xhtml_dehyph_temp_dir,
        dictionary_file_path,
        no_accent_dict_file_path,
        spellcheck_file_path,
        verbose,
    )
    spellchecked_xhtml_temp_dir = tempfile.mkdtemp()
    if verbose:
        print(
            "temp dir for collecting xar context, including spellchecked hocr: ",
            spellchecked_xhtml_temp_dir,
        )
    spellcheck_hocr.spellcheck(
        spellcheck_file_path,
        xhtml_dehyph_temp_dir,
        spellchecked_xhtml_temp_dir,
        verbose,
    )
    spinner.stop()
    # todo delete temp files
    # make meta file for texts
    xsl_file = Path(__file__).parent / "XSLT/make_meta_texts.xsl"
    xsl_file_handle = open(xsl_file, "r")
    dom = ET.parse(xsl_file_handle)  # ET.parse(open(metadata_file, 'r'))
    xslt = ET.parse(open(xsl_file, "r"))
    plain_string_value = etree.XSLT.strparam(identifier)
    transform = ET.XSLT(xslt)
    newdom = transform(
        dom,
        identifier=etree.XSLT.strparam(identifier),
        classifier=etree.XSLT.strparam(classifier),
        rundate=etree.XSLT.strparam(datetime),
        engine=etree.XSLT.strparam(ocr_engine),
    )
    newdom.write(
        os.path.join(spellchecked_xhtml_temp_dir, "meta.xml"), pretty_print=True
    )

    # make repo.xml for texts
    # xsl_file = Path(__file__).parent / "XSLT/make_repo_texts.xsl"
    # xsl_file_handle = open(xsl_file, "r")
    # xslt = ET.parse(xsl_file_handle)
    # dom = ET.parse(open(xsl_file, "r"))
    # get accuracy value
    assessment = str(assess_hocr_dir.assess(spellchecked_xhtml_temp_dir))
    # transform = ET.XSLT(xslt)
    # newdom = transform(dom, identifier=etree.XSLT.strparam(identifier), accuracy=assessment, rundate=etree.XSLT.strparam(datetime))
    # newdom.write(os.path.join(spellchecked_xhtml_temp_dir,'repo.xml') , pretty_print=True)
    # different approach
    with open(os.path.join(spellchecked_xhtml_temp_dir, "repo.xml"), "w") as repo_file:
        repo_file.write(repo_file_string)

    if not (imagexarfile.name == None):
        accuracySvgAndTotals.makeAccuracySVG(
            spellchecked_xhtml_temp_dir, imagexarfile.name
        )

    # make expath-pkg.xml for texts
    xsl_file = Path(__file__).parent / "XSLT/make_expath_texts.xsl"
    xsl_file_handle = open(xsl_file, "r")
    dom = ET.parse(open(xsl_file, "r"))
    xslt = ET.parse(xsl_file_handle)
    transform = ET.XSLT(xslt)
    newdom = transform(
        dom,
        identifier=etree.XSLT.strparam(identifier),
        rundate=etree.XSLT.strparam(datetime),
    )
    newdom.write(
        os.path.join(spellchecked_xhtml_temp_dir, "expath-pkg.xml"), pretty_print=True
    )

    # save static metadata files to the temp dir
    static_files_dir = Path(__file__).parent / "static_for_text_xar"
    static_files = os.listdir(static_files_dir)
    for file_name in static_files:
        shutil.copy(
            os.path.join(static_files_dir, file_name), spellchecked_xhtml_temp_dir
        )

    # make accuracy report?
    accuracySvgAndTotals.makeTotalsFile(spellchecked_xhtml_temp_dir)
    # this requires the xar file, or at least images.
    # We could re-do all this by passing in the image xar file and using its metadata for this one, which would
    # mean we don't have to keep our metadata files sitting around.
    # generate the zip file and save to outputdir

    # Make xar file output by compressing everything in 'spellchecked_xhtml_temp_dir'
    output_zip_file_path = os.path.join(
        output_dir, identifier + "-" + datetime + "-" + classifier + "-texts.xar"
    )
    with ZipFile(output_zip_file_path, "w") as zipObj:
        for filename in os.listdir(spellchecked_xhtml_temp_dir):
            filePath = os.path.join(spellchecked_xhtml_temp_dir, filename)
            zipObj.write(filePath, basename(filePath))
    print("text archive from date", datetime, "saved to", output_zip_file_path)

    # Clean up
    if not (verbose):
        for temp_directory in [spellchecked_xhtml_temp_dir, xhtml_dehyph_temp_dir]:
            shutil.rmtree(temp_directory)
        # delete unused spellcheck file
        os.remove(spellcheck_file_path)
    # done function to generate text xar


# Helper functions
def generate_image_expath(identifier):
    return f"""<pkg:package xmlns:pkg="http://expath.org/ns/pkg" version="1" spec="1.0" name="http://heml.mta.ca/Lace/Images/{identifier}" abbrev="{identifier}">
      <pkg:title>{identifier}: OCR Images</pkg:title>
      <pkg:dependency package="http://heml.mta.ca/Lace/application" semver-min="0.6.17">
      </pkg:dependency>
    </pkg:package>"""


def generate_image_meta(metadata_file_handle):
    from pathlib import Path

    xsl_file = Path(__file__).parent / "XSLT/make_meta_images.xsl"
    xsl_file_handle = open(xsl_file, "r")
    return xslt(xsl_file_handle, metadata_file_handle)


def xslt(xsl_file, xml_file):
    import lxml.etree as ET

    dom = ET.parse(xml_file)
    xslt = ET.parse(xsl_file)
    transform = ET.XSLT(xslt)
    # print(transform.error_log)
    newdom = transform(dom)
    return ET.tostring(newdom, pretty_print=True)


def generate_image_repo(metadata_file):
    from pathlib import Path

    xsl_file = Path(__file__).parent / "XSLT/make_repo_images.xsl"
    xsl_file_handle = open(xsl_file, "r")
    return xslt(xsl_file_handle, metadata_file)


def binarize_skimage(filein_path, fileout_path, verbose):
    # TODO: make regional otsu
    import skimage
    from skimage import io
    from skimage.filters import threshold_otsu

    if verbose:
        print("input file to binarize: ", filein_path)
    try:
        image = io.imread(filein_path)
    except Exception as ex:
        print("raised exception trying to read: ", type(ex))
    try:
        thresh = threshold_otsu(image)
        binary_image = image > thresh
        skimage.io.imsave(fileout_path, binary_image)
    except ValueError:
        print("Error binarizing file ", filein_path, ". Passing it through unchanged.")
        skimage.io.imsave(fileout_path, image)


# text helper functions
def get_dc_element_from_metadata(element_name, etree_root):
    return etree_root.xpath(
        "//dc:" + element_name,
        namespaces={
            "lace": "http://heml.mta.ca/2019/lace",
            "dc": "http://purl.org/dc/elements/1.1/",
        },
    )[0].text


def make_text_repo_string(etree_root, datetime):
    lookup = {}
    for element_name in ["creator", "date", "identifier"]:
        lookup[element_name] = get_dc_element_from_metadata(element_name, etree_root)
    return f"""<repo:meta xmlns:repo="http://exist-db.org/xquery/repo" xmlns:dc="http://purl.org/dc/elements/1.1/">
  <repo:description>OCR run on {datetime} of {lookup['creator']} ({lookup['date']})  </repo:description>
  <repo:author>Bruce Robertson brobertson@mta.ca</repo:author>
  <repo:website>http://heml.mta.ca/Lace</repo:website>
  <repo:status>beta</repo:status>
  <repo:copyright>true</repo:copyright>
  <repo:license>GNU-LGPL</repo:license>
  <repo:type>library</repo:type>
  <repo:target>{lookup['identifier']}_{datetime}</repo:target>
  <repo:prepare>pre-install.xql</repo:prepare>
  <repo:permissions user="guest" group="guest" mode="rw-rw-rw-"/>
  <repo:finish>post-install.xql</repo:finish>
</repo:meta>"""
