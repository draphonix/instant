import click
from instant.services.img.img_helper import ImageHelper

@click.group()
def cli():
    """Image CLI commands."""
    pass

@cli.command()
@click.argument('image_path', type=click.Path(exists=True))
def generate_icon(image_path):
    """
    Command-line interface for generating Apple Icon Set from an image.
    
    IMAGE_PATH: The path to the source image.
    """
    ImageHelper.generate_mac_icon(image_path)

if __name__ == "__main__":
    cli()