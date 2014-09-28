class Bean():

    file_name = None
    file_path = None
    download_type = None
    label = None
    size = None
    ftp_base_url = None
    ftp_data_dir = None
    file_list = []
    thread = False

    def __init__(self, file_name, file_path, download_type, label, size, ftp_base_url, ftp_data_dir, file_list, thread):
        self.file_name = file_name
        self.file_path = file_path
        self.download_type = download_type
        self.label = label
        self.size = size
        self.ftp_base_url = ftp_base_url
        self.ftp_data_dir = ftp_data_dir
        self.file_list = file_list
        self.thread = thread