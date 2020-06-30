# -*- coding: utf-8 -*-

"""
This module contains a quick and dirty Plotter class for creating uniform plots for the report.
Furthermore Color-Mappers were inteded for supporting different colormappings in pygal-plots.
"""

from abc import ABC, abstractmethod
from copy import deepcopy
import os.path

import pygal
from pygal.style import Style
from pandas import Series


class ColorMapper(ABC):
    """ abstract class for different implementations of color-mappers """
    @abstractmethod
    def normalize(self, vmin, vmax):
        "used for normalization of the color-map before values get mapped"

    @abstractmethod
    def get_color(self, val):
        "mapping of values to their corresponding colorstrings"


class RedGreenMapper(ColorMapper):
    """
    Simple ColorMapper which maps positive values to green and negative values to red.
    """

    def __init__(self):
        super(RedGreenMapper, self).__init__()
        self.neg_col = '#F44336'
        self.pos_col = '#009688'

    def normalize(self, vmin, vmax):
        pass

    def get_color(self, val):
        """ maps positive values to green and negative values to red"""
        if val < 0:
            return self.neg_col
        # elif val >= 0:
        return self.pos_col


class ReportPlotter(object):
    """
    Simple Plotter class for making the plots for the report look all uniformly.

    Attributes
    ----------
    out_dir: str
        output-directory
    style: pygal.style.Style
    config: pygal.Config
    default_fname: str
        name of the plots if no name or title is supplied
    format: ['png', 'svg']
        outputformat of plots
    cmapper: ColorMapper


    Methods
    -------
    set_label_rot(rot)
        sets the label rotation of the main axis
    export_bar_plot(df, title='', y_title='', x_title='', horizontal=False, use_colmap=False)
        create a bar-plot
    export_line_plot(df, title='', y_title='', x_title='', use_colmap=False)
        create a line plot
    export_horizontal_bar_plot(*args, **kwargs)
        create a bar-plot with horizontal bars

    """

    def __init__(self, out_dir, o_format='png', x_rot=0, label_size=14, title_size=18,
                 cmapper=RedGreenMapper()):
        """

        Parameters:
        -----------
        out_dir: str
            output-directory
        o_format: 'png' or 'svg'
            outputformat of plots
        x_rot: int
            rotation of x-labels
        label_size: int
        title_size: int
        cmapper: ColoMapper, RedGreenMapper

        """

        self.out_dir = out_dir
        self.style = Style()
        self.style.label_font_size = self.style.major_label_font_size = label_size
        self.style.title_font_size = title_size
        self.style.background = 'transparent'

        self.config = pygal.Config()
        self.config.x_label_rotation = x_rot
        self.config.width = 1200

        self.default_fname = 'no_name'

        if o_format not in ['png', 'svg']:
            raise ValueError(
                "Format %s not supported. Must be either svg or png" %
                o_format)
        self.format = o_format

        self.cmapper = cmapper

    def set_label_rot(self, rot):
        """ sets the label rotation of the main axis """
        self.config.x_label_rotation = rot

    def __render(self, chart, name):
        """ private method for rendering to file """
        name = name.replace(' ', '_')
        if self.format == 'svg':
            chart.render_to_file(os.path.join(self.out_dir, '%s.svg' % name))
        elif self.format == 'png':
            chart.render_to_png(os.path.join(self.out_dir, '%s.png' % name))

    def __normalize_colormapper(self, df):
        """ all normalization of colormapper based on existing values """
        self.cmapper.normalize(df.values.min, df.values.max)

    def __map_vals_to_color(self, vals):
        """
        map values to their colorstrings and return a dict with value and css-formatstring for
		pygal-plotter
        """
        return [{'value': val, 'style': 'fill: %s' % colstr} for val, colstr in zip(
            vals, map(self.cmapper.get_color, vals))]

    def __add_valcol(self, chart, name, vals, use_colmap):
        """
        adds a column of datates to a chart
        """
        if use_colmap:
            plot_dict = self.__map_vals_to_color(vals)
            chart.add(name, plot_dict)
        else:
            chart.add(name, vals)

    def export_bar_plot(self, df, title='', y_title='',
                        x_title='', horizontal=False, use_colmap=False):
        """
        creates a bar-plot based on data-supplied

        Parameters:
        -----------
        df: pandas.DataFrame or pandas.Series
            data to be plotted
        title: str
            main title of the plot
        y_title: str
            title of the y-axis
        x_title: str
            title of the x-axis
        horizontal: bool
            whether to create a horizontal bar plot
        use_colmap: bool
            whether to use pygals-default coloring or to use a colormapper (colors based on values)

        Returns:
        --------
        None

        """
        chart = pygal.HorizontalBar if horizontal else pygal.Bar

        if horizontal:
            config = deepcopy(self.config)
            config.y_label_rotation = self.config.x_label_rotation
            config.x_label_rotation = self.config.y_label_rotation
            config.height = self.config.width
        else:
            config = self.config

        bar_chart = chart(
            config,
            y_title=y_title,
            x_title=x_title,
            style=self.style)
        bar_chart.title = title
        bar_chart.x_labels = df.index
        if isinstance(df, Series):
            self.__add_valcol(bar_chart, df.name, df.values, use_colmap)
        # a DataFrame:
        else:
            for col in df.columns:
                self.__add_valcol(bar_chart, col, df[col], use_colmap)
        self.__render(bar_chart, title or y_title or self.default_fname)

    def export_horizontal_bar_plot(self, *args, **kwargs):
        """ creates a horizontal bar plot based on the data supplied """
        self.export_bar_plot(*args, horizontal=True, **kwargs)

    def export_line_plot(self, df, title='', y_title='',
                         x_title='', use_colmap=False):
        """
        creates a line plot based on the data supplied

        Parameters:
        -----------
        df: pandas.DataFrame, pandas.Series
            data to be plotted
        title: str
            main title of the plot
        y_title: str
            title of the y-axis
        x_title: str
            title of the x-axis
        use_colmap: bool
            whether to use pygals-default coloring or to use a colormapper (colors based on values)

        Returns:
        --------
        None

        """
        line_chart = pygal.Line(
            self.config,
            y_title=y_title,
            x_title=x_title,
            style=self.style)
        line_chart.title = title
        line_chart.x_labels = df.index
        if isinstance(df, Series):
            self.__add_valcol(line_chart, df.name, df.values, use_colmap)
        # a DataFrame:
        else:
            for col in df.columns:
                self.__add_valcol(line_chart, col, df[col], use_colmap)
        self.__render(line_chart, title or y_title or self.default_fname)
