# -*- coding: utf-8 -*-

from pprint import pprint

import click

from . import __version__
from .io import read_pdf


class Config(object):
    def  __init__(self):
        self.config = {}

    def set_config(self, key, value):
        self.config[key] = value


pass_config = click.make_pass_decorator(Config)


@click.group()
@click.version_option(version=__version__)
@click.option('-p', '--pages', default='1', help='Comma-separated page numbers.'
              ' Example: 1,3,4 or 1,4-end.')
@click.option('-o', '--output', help='Output file path.')
@click.option('-f', '--format',
              type=click.Choice(['csv', 'json', 'excel', 'html']),
              help='Output file format.')
@click.option('-z', '--zip', is_flag=True, help='Create ZIP archive.')
@click.option('-split', '--split_text', is_flag=True,
              help='Split text that spans across multiple cells.')
@click.option('-flag', '--flag_size', is_flag=True, help='Flag text based on'
              ' font size. Useful to detect super/subscripts.')
@click.option('-M', '--margins', nargs=3, default=(1.0, 0.5, 0.1),
              help='PDFMiner char_margin, line_margin and word_margin.')
@click.pass_context
def cli(ctx, *args, **kwargs):
    """Camelot: PDF Table Extraction for Humans"""
    ctx.obj = Config()
    for key, value in kwargs.iteritems():
        ctx.obj.set_config(key, value)


@cli.command('lattice')
@click.option('-T', '--table_area', default=[], multiple=True,
              help='Table areas to process. Example: x1,y1,x2,y2'
              ' where x1, y1 -> left-top and x2, y2 -> right-bottom.')
@click.option('-back', '--process_background', is_flag=True,
              help='Process background lines.')
@click.option('-scale', '--line_size_scaling', default=15,
              help='Line size scaling factor. The larger the value,'
              ' the smaller the detected lines.')
@click.option('-copy', '--copy_text', default=[], type=click.Choice(['h', 'v']),
              multiple=True, help='Direction in which text in a spanning cell'
              ' will be copied over.')
@click.option('-shift', '--shift_text', default=['l', 't'],
              type=click.Choice(['', 'l', 'r', 't', 'b']), multiple=True,
              help='Direction in which text in a spanning cell will flow.')
@click.option('-l', '--line_close_tol', default=2,
              help='Tolerance parameter used to merge close vertical'
              ' and horizontal lines.')
@click.option('-j', '--joint_close_tol', default=2,
              help='Tolerance parameter used to decide whether'
              ' the detected lines and points lie close to each other.')
@click.option('-block', '--threshold_blocksize', default=15,
              help='For adaptive thresholding, size of a pixel'
              ' neighborhood that is used to calculate a threshold value for'
              ' the pixel. Example: 3, 5, 7, and so on.')
@click.option('-const', '--threshold_constant', default=-2,
              help='For adaptive thresholding, constant subtracted'
              ' from the mean or weighted mean. Normally, it is positive but'
              ' may be zero or negative as well.')
@click.option('-I', '--iterations', default=0,
              help='Number of times for erosion/dilation will be applied.')
@click.option('-plot', '--plot_type',
              type=click.Choice(['text', 'table', 'contour', 'joint', 'line']),
              help='Plot geometry found on PDF page, for debugging.')
@click.argument('filepath', type=click.Path(exists=True))
@pass_config
def lattice(c, *args, **kwargs):
    """Use lines between text to parse the table."""
    conf = c.config
    pages = conf.pop('pages')
    output = conf.pop('output')
    f = conf.pop('format')
    compress = conf.pop('zip')
    plot_type = kwargs.pop('plot_type')
    filepath = kwargs.pop('filepath')
    kwargs.update(conf)

    table_area = list(kwargs['table_area'])
    kwargs['table_area'] = None if not table_area else table_area
    copy_text = list(kwargs['copy_text'])
    kwargs['copy_text'] = None if not copy_text else copy_text
    kwargs['shift_text'] = list(kwargs['shift_text'])

    tables = read_pdf(filepath, pages=pages, flavor='lattice', **kwargs)
    click.echo('Found {} tables'.format(tables.n))
    if plot_type is not None:
        for table in tables:
            table.plot(plot_type)
    else:
        if output is None:
            raise click.UsageError('Please specify output file path using --output')
        if f is None:
            raise click.UsageError('Please specify output file format using --format')
        tables.export(output, f=f, compress=compress)


@cli.command('stream')
@click.option('-T', '--table_area', default=[], multiple=True,
              help='Table areas to process. Example: x1,y1,x2,y2'
              ' where x1, y1 -> left-top and x2, y2 -> right-bottom.')
@click.option('-C', '--columns', default=[], multiple=True,
              help='X coordinates of column separators.')
@click.option('-r', '--row_close_tol', default=2, help='Tolerance parameter'
              ' used to combine text vertically, to generate rows.')
@click.option('-c', '--col_close_tol', default=0, help='Tolerance parameter'
              ' used to combine text horizontally, to generate columns.')
@click.option('-plot', '--plot_type',
              type=click.Choice(['text', 'table']),
              help='Plot geometry found on PDF page for debugging.')
@click.argument('filepath', type=click.Path(exists=True))
@pass_config
def stream(c, *args, **kwargs):
    """Use spaces between text to parse the table."""
    conf = c.config
    pages = conf.pop('pages')
    output = conf.pop('output')
    f = conf.pop('format')
    compress = conf.pop('zip')
    plot_type = kwargs.pop('plot_type')
    filepath = kwargs.pop('filepath')
    kwargs.update(conf)

    table_area = list(kwargs['table_area'])
    kwargs['table_area'] = None if not table_area else table_area
    columns = list(kwargs['columns'])
    kwargs['columns'] = None if not columns else columns

    tables = read_pdf(filepath, pages=pages, flavor='stream', **kwargs)
    click.echo('Found {} tables'.format(tables.n))
    if plot_type is not None:
        for table in tables:
            table.plot(plot_type)
    else:
        if output is None:
            raise click.UsageError('Please specify output file path using --output')
        if f is None:
            raise click.UsageError('Please specify output file format using --format')
        tables.export(output, f=f, compress=compress)