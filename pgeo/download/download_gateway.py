

def download(source,
             download_beans,
             thread_group_id=None,
             aggregation=None,
             username=None,
             password=None):
    """

    @param source: Data source code, e.g. 'modis'
    @type source: String
    @param download_beans: Configuration beans containing the information to download the layer(s)
    @type download_beans: Array od DownloadBean
    @param thread_group_id: An id to monitor the progress of the threads.
    @type thread_group_id: String
    @param aggregation: Used to aggregate the layers at the end of the download, e.g. 'avg'
    @type aggregation: String
    @param username: Used to access the data source.
    @type username: String
    @param password: Used to access the data source.
    @type password: String
    """
    pass