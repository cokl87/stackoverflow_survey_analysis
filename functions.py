# -*- coding: utf-8 -*-

"""
This module contains all generalized functions used in the notebooks for
analysisng the stackoverflow-data
"""

# ----------------------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------------------

import zipfile
import json
import pandas as pd


# ----------------------------------------------------------------------------
# CONSTANTS
# ----------------------------------------------------------------------------

JSON_PTH = './data/input/stackoverflow/survey_pathes.json'


# ----------------------------------------------------------------------------
# FUNCTIONS
# ----------------------------------------------------------------------------

def get_survey_year(year):
    """
    function which reads the ćsv-file with survey results of specified year
    into a dataframe

    Parameters:
    -----------
    year: int, str
        year of survey to be read

    Returns:
    --------
    pandas.DataFrame
        Dataframe with survey-results of specified year
    """

    # read dictionary with pathes and names of survey-data created in first
    # notebook 'screening_of_data.ipynb'
    # attach dict to function-object as attribute, so that file has to be
    # read only once
    if not hasattr(get_survey_year, 'pths'):
        with open(JSON_PTH, 'r') as json_in:
            get_survey_year.pths = json.load(json_in)

    # try to convert input to str
    year = str(year)

    if year not in get_survey_year.pths:
        return pd.DataFrame()

    # get path to zipfile and name of main survey-data according to dict. Read
    # the specified data into a dataframe
    ydict = get_survey_year.pths.get(year)
    with zipfile.ZipFile(ydict.get('zpth'), mode='r') as zfile:
        with zfile.open(ydict.get('fname'), mode='r') as fin:
            return pd.read_csv(fin, encoding='latin-1', low_memory=False)


def get_fraction_of_answers(data, col, sep=';'):
    """
    Calculates the percentage of participants giving a certain answer. If
    necessary splits the answers by a separator in case where several
    answers could be selected.

    Parameters:
    -----------
    data: pandas.DataFrame
        Dataframe to be analysed
    col: str
        name of the column which asnwers to be analysed

    Returns:
    --------
    pd.Series
        Series with value fractions (how many participants gave that answer)

    """
    data.dropna(subset=[col], inplace=True)
    n_rows = data.shape[0]
    if sep:
        # split entries by separation sign and stack the so created columns to
        # one; then count all values
        return data[col].apply(
            lambda x: pd.Series(x.split(sep))
        ).stack().value_counts() / float(n_rows)
    # 'else': count all values and devide by number of answers
    return data[col].value_counts() / float(n_rows)
