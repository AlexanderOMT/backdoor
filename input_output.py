
#!/usr/bin/env python

import sys

class CustomStandardStream():

    def __init__(self, thread_read_name, thread_write_name) -> None:
        self.thread_read_name = thread_read_name
        self.thread_write_name = thread_write_name

    def handle_io(self, thread_name, notify = None):
        sys.stdout.write('\x1b[2K')
        if thread_name == self.thread_write_name:
            sys.stdout.write(f'\r{notify} >> ')
            return input() 
        else:
            sys.stdout.write(f'\r[+] Server read:\n\n{notify}\n')

class CustomIOException(Exception):
    pass