
#!/usr/bin/env python

import sys

class CustomStandardStream():

    def __init__(self, thread_read_name, thread_write_name) -> None:
        self.thread_read_name = thread_read_name
        self.thread_write_name = thread_write_name
        self.send_to = ''

    def handle_io(self, thread_name, notify = None):
        # TODO refractor : self.send_to and notify are not well programmed
        sys.stdout.write('\x1b[2K') 
        if thread_name == self.thread_write_name:
            self.send_to = notify
            sys.stdout.write(f'\r{self.send_to} >> ')
            res = ''
            for line in sys.stdin.readline(): 
                res += line
            return res

        else:
            sys.stdout.write(f'\r\r<< Server read:\n\n{notify}\n')
            sys.stdout.write(f'\r{self.send_to} >> ')

    class CustomIOException(Exception):
        pass