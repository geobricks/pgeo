from ftplib import FTP
from threading import Thread
from threading import Lock
import Queue
import os
import time
from threading import Timer
from pgeo.utils import log
from pgeo.utils.filesystem import create_filesystem
from pgeo.gis.gdal_calc import calc_layers


log = log.logger('bulk_download_threads_manager.py')
progress_map = {}
exit_flags = {}


class BulkDownloadThread(Thread):

    bulk_download_object = None
    total_files = 0
    downloaded_files = 0
    aggregation = None

    def __init__(self, thread_name, queue, queue_lock, tab_id, target_folder, aggregation):

        Thread.__init__(self)

        self.thread_name = thread_name
        self.queue = queue
        self.queue_lock = queue_lock
        self.tab_id = tab_id
        self.target_folder = target_folder
        self.aggregation = aggregation

        progress_map[self.tab_id] = {}
        progress_map[self.tab_id]['status'] = 'WAITING'

    def run(self):

        while not exit_flags[self.tab_id]:

            self.queue_lock.acquire()

            if not self.queue.empty():

                self.bulk_download_object = self.queue.get()
                self.total_files = len(self.bulk_download_object['file_list'])
                progress_map[self.tab_id]['total_files'] = self.total_files
                progress_map[self.tab_id]['downloaded_files'] = 0
                progress_map[self.tab_id]['status'] = 'START'
                progress_map[self.tab_id]['progress'] = 0

                self.queue_lock.release()

                self.target_folder = create_filesystem('trmm2', self.bulk_download_object['filesystem_structure'])

                ftp = FTP(self.bulk_download_object['ftp_base_url'])

                try:
                    ftp.login()
                except Exception, e:
                    progress_map[self.tab_id]['status'] = 'ERROR'
                    exit_flags[self.tab_id] = 1
                    log.error(e)
                    continue

                ftp.cwd(self.bulk_download_object['ftp_data_dir'])
                remote_files = ftp.nlst()

                for file_name in self.bulk_download_object['file_list']:

                    log.info('Downloading: ' + file_name['file_name'])

                    if file_name['file_name'] in remote_files:


                        ftp.sendcmd('TYPE i')
                        file_obj = file_name['file_name']
                        local_file = os.path.join(self.target_folder, file_obj)
                        progress_map[self.tab_id]['status'] = 'ONGOING'

                        if not os.path.isfile(local_file):

                            with open(local_file, 'w') as f:

                                def callback(chunk):
                                    f.write(chunk)
                                ftp.retrbinary('RETR %s' % file_obj, callback)
                                self.downloaded_files += 1
                                progress_map[self.tab_id]['status'] = 'COMPLETE'
                                progress_map[self.tab_id]['progress'] = self.percent_done()

                        else:
                            self.downloaded_files += 1
                            progress_map[self.tab_id]['status'] = 'COMPLETE'
                            progress_map[self.tab_id]['progress'] = self.percent_done()

                ftp.quit()
                log.info('Download Complete. Start aggregation.')
                self.aggregate_layers()

            else:

                self.queue_lock.release()

            time.sleep(1)

    def percent_done(self):
        return float('{0:.2f}'.format(float(self.downloaded_files) / float(self.total_files) * 100))

    def aggregate_layers(self):
        if self.aggregation is not None:
            file_name = self.target_folder + '/'
            file_name += self.bulk_download_object['filesystem_structure']['year']
            file_name += self.bulk_download_object['filesystem_structure']['month']
            file_name += self.bulk_download_object['filesystem_structure']['day']
            file_name += '_' + self.aggregation.upper()
            file_name += '.geotif'
            input_files = [self.target_folder + '/' + x['file_name'] for x in self.bulk_download_object['file_list'] if '.tif' in x['file_name']]
            calc_layers(input_files, file_name, self.aggregation)


class BulkDownloadManager(Thread):

    def __init__(self, source, filesystem_structure, bulk_download_objects, tab_id, aggregation):
        Thread.__init__(self)
        self.bulk_download_objects = bulk_download_objects
        self.tab_id = tab_id
        self.source = source
        self.filesystem_structure = filesystem_structure
        # self.target_folder = create_filesystem(self.source, self.filesystem_structure)
        self.target_folder = 'WORK IN PROGRESS'
        self.aggregation = aggregation

    def run(self):
        t = Timer(1, self.start_manager)
        t.start()
        return self.target_folder

    def start_manager(self):

        exit_flags[self.tab_id] = 0

        log.info('START | Bulk Download Manager')

        # thread_list = ['Alpha', 'Bravo', 'Charlie', 'Delta', 'Echo', 'Foxtrot', 'Golf', 'Hotel', 'India', 'Juliet']
        thread_list = ['Alpha']
        queue_lock = Lock()
        work_queue = Queue.Queue(len(self.bulk_download_objects))
        threads = []

        for thread_name in thread_list:
            thread = BulkDownloadThread(thread_name, work_queue, queue_lock, self.tab_id, self.target_folder, self.aggregation)
            thread.start()
            threads.append(thread)

        queue_lock.acquire()
        for obj in self.bulk_download_objects:
            work_queue.put(obj)
        queue_lock.release()

        while not work_queue.empty():
            pass

        exit_flags[self.tab_id] = 1

        for t in threads:
            t.join()

        log.info('END   | Bulk Download Manager')


class BulkDownloadObject():

    ftp_base_url = None
    ftp_data_dir = None
    file_list = []

    def __init__(self, ftp_base_url, ftp_data_dir, file_list):
        self.ftp_base_url = ftp_base_url
        self.ftp_data_dir = ftp_data_dir
        self.file_list = file_list

    def __str__(self):
        s = ''
        s += str(self.ftp_base_url) + '\n'
        s += str(self.ftp_data_dir) + '\n'
        s += str(self.file_list)
        return s