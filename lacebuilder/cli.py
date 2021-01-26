"""Console script for lacebuilder."""
import sys
import click
from .lacebuilder import * 
@click.group(chain=True)
@click.option("--outputdir", type=click.Path(exists=True,dir_okay=True,file_okay=False,writable=True), help='the directory in which the output packages will be put.', required=True)
@click.option("--metadatafile", type=click.File(mode='r'), help='an xml metadata file for the image set corresponding to this packaging.')
@click.pass_context
def main(ctx, outputdir, metadatafile):
    ctx.ensure_object(dict)
    ctx.obj = {
        'outputdir': outputdir,
        'metadatafile': metadatafile,
    }
    pass


@main.command()
@click.pass_context
@click.option("--imagedir", type=click.Path(exists=True,dir_okay=True,file_okay=False,readable=True), help='the directory in which the images to be packaged are found.', required=True)
#@click.option("--metadatafile", type=click.File(mode='r'), help='an xml metadata file for this image set. If this file is not given, one will be generated for you using a command line dialog.')
#@click.option("--outputdir", type=click.Path(exists=True,dir_okay=True,file_okay=False,writable=True), help='the directory in which the output packages will be put.', required=True)
@click.option('--verbose', is_flag=True, help="Will print verbose messages.")
@click.option('--clobber', is_flag=True, help="Will overwrite existing file.")
def packImages(ctx, imagedir, verbose, clobber):
    """Generate image xar files for Lace."""
    #this is set at the main command, so we need to access it here
    outputdir = ctx.obj['outputdir']
    print("outputdir:", outputdir)
    metadatafile = ctx.obj['metadatafile']
    print("metadata file:", metadatafile)
    if verbose:
        click.echo("image inputdir is " + imagedir)
        click.echo("iamge output dir is " + outputdir)
    #note we convert the metadatafile handle to a string because it is used multiple times 
    #in this function, and will fail its reads after the first time otherwise
    generate_image_xar(imagedir, outputdir, metadatafile.name, verbose, clobber)
    #make_metadata_file()
    return 0

@main.command()
@click.pass_context
@click.option('--hocrdir', type=click.Path(exists=True,dir_okay=True,file_okay=False,readable=True), help='the directory in which the hocr files (suffixed with .hocr, .html or .htm) are found.', required=True)
#@click.option("--outputdir", type=click.Path(exists=True,dir_okay=True,file_okay=False,writable=True), help='the directory in which the output packages will be put.', required=True)
#@click.option("--metadatafile", type=click.File(mode='r'), help='The xml metadata file defining the images that generated this OCR run.')
@click.option("--imagexarfile", type=click.File(mode='r'), help='The xar file of the images that generated this OCR run.')
@click.option("--dictionaryfile", type=click.File(mode='r'), help='The name of the dictionary file to be used to correct this OCR run.')
@click.option('--ocr-engine',
              type=click.Choice(['kraken', 'tesseract', 'ocropus'], case_sensitive=False), default='kraken')
@click.option("--classifier", type=str, required=True, help='a string identifying the classifier used to generate this OCR run.')
@click.option("--datetime", type=click.DateTime(formats=['%Y-%m-%d-%H-%M-%S']), help='the datetime on which this OCR run was generated. If this is omitted, then the datetime at which the data was processed with lacebuilder will be used instead.')
@click.option('--verbose', is_flag=True, help="Will print verbose messages.")
@click.option('--clobber', is_flag=True, help="Will overwrite existing file.")
def packTexts(ctx, hocrdir, imagexarfile, dictionaryfile, ocr_engine, classifier, datetime, verbose, clobber):
    """Generate text xar files for Lace."""
    #this is set at the main command, so we need to access it here
    outputdir = ctx.obj['outputdir']
    metadatafile = ctx.obj['metadatafile']
    if (metadatafile == None) and (imagexarfile == None):
        print(ctx.parent.get_help())
        print(ctx.get_help())
        print("Error: you must provide either a --metadatafile or a --imagexarfile to the packtexts command.")
        exit(0)
    generate_hocr_xar(hocrdir, outputdir, metadatafile, imagexarfile, dictionaryfile, ocr_engine, classifier, datetime, verbose, clobber)
    return 0

if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
