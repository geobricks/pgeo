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


thread_manager_processes = {}
progress_map = {}
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


def create_structure(source, product, year, day):
    print 'CALL FILESYSTEM!!!'


class LayerDownloadThread(Thread):

    file_obj = None
    file_name = None
    file_path = None
    total_size = 0
    download_size = 0

    def __init__(self, source, thread_name, queue, queue_lock, key, block_sz=16384):

        Thread.__init__(self)

        self.thread_name = thread_name
        self.queue = queue
        self.queue_lock = queue_lock
        self.key = key
        self.block_sz = block_sz
        self.source = source
        self.conf = read_config_file_json(self.source, 'data_providers')

    def run(self):

        while not exit_flag:

            self.queue_lock.acquire()

            if not self.queue.empty():

                self.file_obj = self.queue.get()
                self.file_name = self.file_obj['file_name']
                self.file_path = self.file_obj['file_path']
                self.download_size = 0
                if self.file_name not in progress_map:
                    out_template['thread'] = self.thread_name
                    out_template['layer_name'] = self.file_name
                    progress_map[self.file_name] = out_template
                self.queue_lock.release()

                local_file = os.path.join(self.conf['target']['target_dir'], self.file_name)
                u = urllib2.urlopen(self.file_path)
                f = open(local_file, 'wb')

                if 'size' in self.file_obj:
                    self.total_size = self.file_obj['size']
                else:
                    meta = u.info()
                    self.total_size = int(meta.getheaders('Content-Length')[0])

                progress_map[self.file_name]['total_size'] = self.total_size
                if 'download_size' not in progress_map[self.file_name]:
                    progress_map[self.file_name]['download_size'] = 0

                file_size_dl = 0
                while self.percent_done() < 100:
                    chunk = u.read(self.block_sz)
                    if not buffer:
                        break
                    file_size_dl += len(chunk)
                    f.write(chunk)
                    self.download_size += len(chunk)
                    progress_map[self.file_name]['download_size'] = progress_map[self.file_name]['download_size'] + len(chunk)
                    progress_map[self.file_name]['progress'] = float('{0:.2f}'.format(float(progress_map[self.file_name]['download_size']) / float(progress_map[self.file_name]['total_size']) * 100))
                    progress_map[self.file_name]['status'] = 'DOWNLOADING'
                    progress_map[self.file_name]['key'] = self.key
                    # log.info(self.thread_name + ' is processing: ' + self.file_name)
                    # log.info('\tProgress: ' + str(self.percent_done()) + '%')

                progress_map[self.file_name]['status'] = 'COMPLETE'
                f.close()

            else:
                self.queue_lock.release()

            time.sleep(1)

    def percent_done(self):
        return float('{0:.2f}'.format(float(self.download_size) / float(self.total_size) * 100))


class Manager(Thread):

    def __init__(self, source, file_paths_and_sizes):
        Thread.__init__(self)
        self.source = source
        self.file_paths_and_sizes = file_paths_and_sizes

    def run(self):
        t = Timer(1, self.start_manager)
        t.start()

    def start_manager(self):

        global exit_flag
        exit_flag = 0

        global name_list
        name_list = self.file_paths_and_sizes

        log.info('START | Layers Download Manager')

        thread_list = ['Alpha', 'Bravo', 'Charlie', 'Delta', 'Echo', 'Foxtrot', 'Golf', 'Hotel', 'India', 'Juliet']
        queue_lock = Lock()
        work_queue = Queue.Queue(len(name_list))
        threads = []

        for tName in thread_list:
            key = str(uuid.uuid4())
            thread = LayerDownloadThread(self.source, tName, work_queue, queue_lock, key)
            thread.start()
            if not threads_map_key in thread_manager_processes:
                thread_manager_processes[threads_map_key] = {}
            thread_manager_processes[threads_map_key][key] = thread
            threads.append(thread)

        queue_lock.acquire()
        for word in name_list:
            work_queue.put(word)
        queue_lock.release()

        while not work_queue.empty():
            pass

        exit_flag = 1

        for t in threads:
            t.join()

        log.info('DONE | Layers Download Manager')