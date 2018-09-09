import pandas as pd
import xarray as xr
import mysql.connector
from mysql.connector import errorcode

cnx = mysql.connector.connect(user='govhack', password='4QD3aJWRtnev5tZf',
                              host='127.0.0.1',
                              database='argi_insur')
cursor = cnx.cursor()

TABLES = {}
TABLES['rainfalls'] = (
    "CREATE TABLE `rainfalls` ("
    "  `station_number` int(11) NOT NULL,"
    "  `area_code` varchar(14) NOT NULL,"
    "  `parameter` varchar(16) NOT NULL,"
    "  `valid_start` date NOT NULL,"
    "  `valid_end` date NOT NULL,"
    "  `value` float NOT NULL,"
    "  `unit` varchar(14) NOT NULL,"
    "  `statistic` varchar(10) NOT NULL,"
    "  `level` varchar(10) NOT NULL,"
    "  `qc_valid_minutes` int(10) NOT NULL,"
    "  `qc_valid_start` date NOT NULL,"
    "  `qc_valid_end` date NOT NULL,"
    ") ENGINE=InnoDB")

# for name, ddl in TABLES.iteritems():
#     try:
#         # print("Creating table {}: ".format(name), end='')
#         cursor.execute(ddl)
#     except mysql.connector.Error as err:
#         if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
#             print("already exists.")
#         else:
#             print(err.msg)
#     else:
#         print("OK")

def epoch_seconds_to_timestamp(inp):
    """
    Converts an integer (seconds since UNIX epoch) or list of integers
    into a Pandas Timestamp object.

    Example:
        >>> epoch_seconds_to_timestamp(1461945600)
        Timestamp('2016-04-29 16:00:00')

        >>> epoch_seconds_to_timestamp([1461945600, 1461945660, 1461945720])
        DatetimeIndex(['2016-04-29 16:00:00', '2016-04-29 16:01:00',
                       '2016-04-29 16:02:00'],
                      dtype='datetime64[ns]', freq=None)
    """
    return pd.to_datetime(inp, unit='s')


def pd_read_fcst_csv(file_path):
    """
    Reads a forecast CSV file and returns a Pandas DataFrame with the
    appropriate type conversions.

    Examples:
        >>> pd_read_fcst_csv('fcst/Op_Official_20150501.csv')
    """
    df = pd.read_csv(file_path)
    for field in ['valid_start', 'valid_end', 'base_time']:
        df[field] = epoch_seconds_to_timestamp(df[field])
    df['station_number'] = df['station_number'].astype('int')

    return df


def pd_read_obs_csv(file_path):
    """
    Reads a observations CSV file and returns a Pandas DataFrame with the
    appropriate type conversions.

    Example:
        >>> pd_read_obs_csv('obs/aws_hourly_20150501.csv')
    """
    df = pd.read_csv(file_path)
    for field in ['valid_start', 'valid_end', 'qc_valid_start', 'qc_valid_end']:
        df[field] = epoch_seconds_to_timestamp(df[field])
    df['station_number'] = df['station_number'].astype('int')

    return df


def dataframe_param_to_xarray(dataframe, param, indices):
    """
    Filters the `dataframe` using its "parameter" column to contain only
    the supplied `param`, then creates an xarray DataArray object using
    the supplied `indices`.

    Example:
        >>> df = pd.DataFrame(
            [[0, 'max', 5],
            [0, 'min', 3],
            [1, 'max', 10],
            [1, 'min, 0]],
            columns=['x', 'parameter', 'value'])
        >>> dataframe_param_to_xarray(df, 'min', ['x'])
        <xarray.DataArray 'min' (x: 2)>
        array([3, 0])
        Coordinates:
          * x        (x) int64 0 1
    """
    # filter by parameter
    dataframe = dataframe[dataframe['parameter'] == param]

    # keep only the indices and value columns
    selection = dataframe[indices + ['value']]

    # drop any spurious duplicated data
    # (the same indices and value, i.e. some data was saved twice?)
    selection = selection.drop_duplicates(subset=indices)

    # drop any spurious NaN-data
    # (indices contain NaN, incomplete data?)
    selection = selection.dropna(subset=indices)

    # set the dataframe index
    selection = selection.set_index(indices)

    # obtain an xarray.DataArray from the 'value' column, using the indices
    # as coordinate values
    data_array = xr.DataArray.from_series(selection["value"])
    data_array.name = param

    return data_array


def fcst_param_to_xarray(dataframe, param, indices=None):
    """
    Filters a forecast dataframe to obtain an xarray DataArray for the specified
    forecast parameter.

    Indices defaults to ['station_number', 'base_time', 'valid_start'], but an
    alternative set of indices can be supplied.

    Example:
        >>> df = pd_read_fcst_csv('fcst/Op_Official_20150501.csv')
        >>> fcst_param_to_xarray(df, 'T')
    """
    if indices is None:
        indices = ['station_number', 'base_time', 'valid_start']
    return dataframe_param_to_xarray(dataframe, param, indices=indices)


def obs_param_to_xarray(dataframe, param, indices=None):
    """
    Filters an observations dataframe to obtain an xarray DataArray for the specified
    observations parameter.

    Indices defaults to ['station_number', 'valid_start'], but an alternative
    set of indices can be supplied.

    Example:
        >>> df = pd_read_obs_csv('obs/aws_hourly_20150501.csv')
        >>> obs_param_to_xarray(df, 'T')
    """
    if indices is None:
        indices = ['station_number', 'valid_start']
    return dataframe_param_to_xarray(dataframe, param, indices=indices)

# df = pd_read_obs_csv('obs/aws_hourly_20171026.csv')
df = pd.read_csv('auspoa06_geocentroids.csv')
# output = obs_param_to_xarray(df, 'T')
print df

# df.to_sql("rainfalls", con=cnx, if_exists='replace')
df.to_sql("auspoa06", con=cnx, if_exists='replace', index=False)

# Make sure data is committed to the database
# cnx.commit()

cursor.close()
cnx.close()
