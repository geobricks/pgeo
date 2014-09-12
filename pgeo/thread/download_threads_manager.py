from threading import Thread
from threading import Lock
import Queue
from pgeo.config.settings import read_config_file_json
import os
import uuid
import time
from threading import Timer
import urllib2
from pgeo.utils import log
from pgeo.utils.filesystem import create_filesystem
from pgeo.error.custom_exceptions import PGeoException


thread_manager_processes = {}
# multi_progress_map = {}
threads_map_key = 'FENIX'
log = log.logger('download_threads_manager.py')
out_template = {
    'download_size': 0,
    'layer_name': 'unknown',
    'progress': 0,
    'total_size': 'unknown',
    'status': 'unknown',
    'thread': 'unknown',
    'key': None
}
exit_flags = {}


class LayerDownloadThread(Thread):

    file_obj = None
    file_name = None
    file_path = None
    total_size = 0
    download_size = 0

    def __init__(self, source, thread_name, queue, queue_lock, key, target_dir, tab_id, multi_progress_map, block_sz=16384):

        Thread.__init__(self)

        self.thread_name = thread_name
        self.queue = queue
        self.queue_lock = queue_lock
        self.key = key
        self.block_sz = block_sz
        self.source = source
        self.conf = read_config_file_json(self.source, 'data_providers')
        self.target_dir = target_dir
        self.tab_id = tab_id
        self.multi_progress_map = multi_progress_map

    def run(self):

        while not exit_flags[self.tab_id]:

            self.queue_lock.acquire()

            if not self.queue.empty():

                self.file_obj = self.queue.get()
                self.file_name = self.file_obj['file_name']
                self.file_path = self.file_obj['file_path']
                self.download_size = 0

                if self.tab_id not in self.multi_progress_map:
                    self.multi_progress_map[self.tab_id] = {}
                # if self.file_name not in multi_progress_map[self.tab_id]:
                self.multi_progress_map[self.tab_id][self.file_name] = {}

                self.queue_lock.release()

                local_file = os.path.join(self.target_dir, self.file_name)

                if 'size' in self.file_obj:
                    self.total_size = self.file_obj['size']
                else:
                    try:
                        u = urllib2.urlopen(self.file_path)
                        meta = u.info()
                        self.total_size = int(meta.getheaders('Content-Length')[0])
                    except:
                        pass

                if self.total_size is None:
                    try:
                        u = urllib2.urlopen(self.file_path)
                        meta = u.info()
                        self.total_size = int(meta.getheaders('Content-Length')[0])
                    except:
                        pass

                # Download the file only if its size is different from the one on the FTP
                allow_layer_download = True
                try:
                    allow_layer_download = int(os.stat(local_file).st_size) < int(self.total_size)
                except OSError, e:
                    pass

                if allow_layer_download:

                    try:

                        u = urllib2.urlopen(self.file_path)
                        meta = u.info()
                        self.total_size = int(meta.getheaders('Content-Length')[0])
                        f = open(local_file, 'wb')

                        self.multi_progress_map[self.tab_id][self.file_name]['total_size'] = self.total_size
                        self.multi_progress_map[self.tab_id][self.file_name]['download_size'] = 0

                        if not os.path.isfile(local_file) or os.stat(local_file).st_size < self.total_size:
                            file_size_dl = 0
                            while self.download_size < self.total_size:
                                chunk = u.read(self.block_sz)
                                if not buffer:
                                    break
                                file_size_dl += len(chunk)
                                f.write(chunk)
                                self.download_size += len(chunk)
                                self.update_progress_map()

                        self.multi_progress_map[self.tab_id][self.file_name]['status'] = 'COMPLETE'
                        f.close()

                    except Exception, e:
                        log.error(str(e))
                        pass

                else:
                    self.multi_progress_map[self.tab_id][self.file_name]['download_size'] = self.total_size
                    self.multi_progress_map[self.tab_id][self.file_name]['progress'] = 100

            else:
                self.queue_lock.release()

            time.sleep(1)

    def percent_done(self):
        return float('{0:.2f}'.format(float(self.download_size) / float(self.total_size) * 100))

    def update_progress_map(self):
        self.multi_progress_map[self.tab_id][self.file_name]['download_size'] = self.download_size
        self.multi_progress_map[self.tab_id][self.file_name]['progress'] = float('{0:.2f}'.format(float(self.multi_progress_map[self.tab_id][self.file_name]['download_size']) / float(self.multi_progress_map[self.tab_id][self.file_name]['total_size']) * 100))
        self.multi_progress_map[self.tab_id][self.file_name]['progress'] = self.percent_done()
        self.multi_progress_map[self.tab_id][self.file_name]['status'] = 'DOWNLOADING'
        self.multi_progress_map[self.tab_id][self.file_name]['key'] = self.key


class Manager(Thread):

    def __init__(self, source, file_paths_and_sizes, filesystem_structure, tab_id):
        """
        Manager for the download threads.
        @param source: e.g. 'MODIS'
        @param file_paths_and_sizes: Array of objects with the following fields:
        ['file_name', 'size', 'label', 'file_path']
        @param filesystem_structure: e.g. {'product': 'MOD13Q1', 'year': '2014', 'day': '033'}
        """
        Thread.__init__(self)
        self.source = source
        self.file_paths_and_sizes = file_paths_and_sizes
        self.filesystem_structure = filesystem_structure
        try:
            self.target_dir = create_filesystem(self.source, self.filesystem_structure)
        except Exception, e:
            log.error(e.message)
            raise PGeoException(e.message, 500)
        self.tab_id = tab_id
        self.multi_progress_map = {}

    def run(self):
        t = Timer(1, self.start_manager)
        t.start()
        return self.target_dir

    def start_manager(self):

        exit_flags[self.tab_id] = 0

        log.info('START | Layers Download Manager')

        thread_list = ['Alpha', 'Bravo', 'Charlie', 'Delta', 'Echo', 'Foxtrot', 'Golf', 'Hotel', 'India', 'Juliet']
        queue_lock = Lock()
        work_queue = Queue.Queue(len(self.file_paths_and_sizes))
        threads = []

        for thread_name in thread_list:
            key = str(uuid.uuid4())
            thread = LayerDownloadThread(self.source, thread_name, work_queue, queue_lock, key, self.target_dir, self.tab_id, self.multi_progress_map)
            thread.start()
            if not threads_map_key in thread_manager_processes:
                thread_manager_processes[threads_map_key] = {}
            thread_manager_processes[threads_map_key][key] = thread
            threads.append(thread)

        queue_lock.acquire()
        for word in self.file_paths_and_sizes:
            work_queue.put(word)
        queue_lock.release()

        while not work_queue.empty():
            pass

        exit_flags[self.tab_id] = 1

        for t in threads:
            t.join()

        log.info('DONE | Layers Download Manager')