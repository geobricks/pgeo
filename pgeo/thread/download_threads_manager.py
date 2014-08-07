from threading import Thread
from threading import Lock
import Queue
from ftplib import FTP
import os
import uuid
import time
from threading import Timer
from pgeo.config.settings import read_config_file_json


thread_manager_processes = {}
progress_map = {}
threads_map_key = 'FENIX'


def create_structure(source, product, year, day):
    print 'CALL FILESYSTEM!!!'


class LayerDownloadThread(Thread):

    layer_name = None
    source_name = None
    total_size = 0
    download_size = 0

    def __init__(self, source_name, product, year, day, thread_name, q, key, queue_lock):

        Thread.__init__(self)

        self.source_name = source_name
        self.thread_name = thread_name
        self.product = product
        self.year = year
        self.day = day
        self.config = read_config_file_json(self.source_name, 'data_providers')
        self.q = q
        self.key = key
        self.queue_lock = queue_lock

    def run(self):

        while not exit_flag:
            self.queue_lock.acquire()
            if not self.q.empty():
                self.layer_name = self.q.get()
                if self.layer_name not in progress_map:
                    progress_map[self.layer_name] = {}
                self.queue_lock.release()
                ftp = FTP(self.confif['source']['ftp']['base_url'])
                ftp.login()
                ftp.cwd(self.config['source']['ftp']['data_dir'] + self.product + '/' + self.year + '/' + self.day + '/')
                ftp.sendcmd('TYPE i')
                total_size = ftp.size(self.layer_name)
                file = self.layer_name
                local_file = os.path.join(self.confif['target']['target_dir'] + '/' + self.product + '/' + self.year + '/' + self.day, file)
                if not os.path.isfile(local_file):
                    try:
                        file_size = os.stat(local_file).st_size
                        if file_size < self.total_size:
                            print 'Downloading ' + str(self.layer_name)
                            with open(local_file, 'w') as f:
                                def callback(chunk):
                                    f.write(chunk)
                                    self.download_size += len(chunk)
                                    progress_map[self.layer_name]['layer_name'] = self.layer_name
                                    progress_map[self.layer_name]['total_size'] = total_size
                                    if 'download_size' not in progress_map[self.layer_name]:
                                        progress_map[self.layer_name]['download_size'] = 0
                                    progress_map[self.layer_name]['download_size'] = progress_map[self.layer_name]['download_size'] + len(chunk)
                                    progress_map[self.layer_name]['progress'] = float(progress_map[self.layer_name]['download_size']) / float(progress_map[self.layer_name]['total_size']) * 100
                                    progress_map[self.layer_name]['status'] = 'DOWNLOADING'
                                ftp.retrbinary('RETR %s' % file, callback)
                    except Exception, e:
                        print 'Downloading ' + str(self.layer_name)
                        with open(local_file, 'w') as f:
                            def callback(chunk):
                                f.write(chunk)
                                self.download_size += len(chunk)
                                progress_map[self.layer_name]['layer_name'] = self.layer_name
                                progress_map[self.layer_name]['total_size'] = total_size
                                if 'download_size' not in progress_map[self.layer_name]:
                                    progress_map[self.layer_name]['download_size'] = 0
                                progress_map[self.layer_name]['download_size'] = progress_map[self.layer_name]['download_size'] + len(chunk)
                                progress_map[self.layer_name]['progress'] = float(progress_map[self.layer_name]['download_size']) / float(progress_map[self.layer_name]['total_size']) * 100
                                progress_map[self.layer_name]['status'] = 'DOWNLOADING'
                            try:
                                ftp.retrbinary('RETR %s' % file, callback)
                            except Exception, e:
                                print 'EXCEPTION DOWNLOADING ' + str(file)
                                print self.config['source']['ftp']['data_dir'] + self.product + '/' + self.year + '/' + self.day + '/' + self.layer_name
                                print e.message
                                print str(e)
                                progress_map[self.layer_name]['status'] = 'ERROR'
                                pass
                ftp.quit()
            else:
                self.queue_lock.release()
            time.sleep(1)

    def percent_done(self):
        return float(self.download_size) / float(self.total_size) * 100


class Manager(Thread):

    def __init__(self, source, product, year, day):
        Thread.__init__(self)
        self.source = source
        self.product = product
        self.year = year
        self.day = day

    def run(self):
        t = Timer(1, self.start_manager)
        t.start()

    def start_manager(self):

        global exit_flag
        exit_flag = 0

        print 'START | Layers Download Manager'

        config = read_config_file_json(self.source, 'data_providers')
        ftp = FTP(config.get('ftp'))
        ftp.login()
        ftp.cwd(config.get('ftp_dir'))
        ftp.cwd(self.product)
        ftp.cwd(self.year)
        ftp.cwd(self.day)
        global name_list
        name_list = ftp.nlst()
        ftp.quit()

        thread_list = ['Alpha', 'Bravo', 'Charlie', 'Delta', 'Echo', 'Foxtrot', 'Golf', 'Hotel', 'India', 'Juliet']
        queue_lock = Lock()
        work_queue = Queue.Queue(len(name_list))
        threads = []

        for tName in thread_list:
            key = str(uuid.uuid4())
            thread = LayerDownloadThread(self.source, self.product, self.year, self.day, tName, work_queue, key, queue_lock)
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

        print 'DONE | Layers Download Manager'