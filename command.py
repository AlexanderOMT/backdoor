#!/usr/bin/env python

from abc import ABC, abstractmethod
import sys



class Command(ABC):
    """
    Command Interface for executing a command
    """

    @abstractmethod
    def execute(self, **args) -> None:
        pass

class Invoker:

    def __init__(self):
        self._commands = {}

    def register(self, command_name: str, command: Command):
        self._commands[command_name] = command

    def execute(self, command_name, **args): 
        if command_name in self._commands.keys():
            self._commands[command_name].execute(args)
        else:
            sys.stdout.write('\x1b[2k[!]Command not Found \x1BE')

class Receiver:
    
    def download_file(self, args):
        sys.stdout.write('\x1b[2k Command Found')

        # TODO refractor
        try:
            with open(args['path'], 'wb') as fd:
                return fd.write(args['content'])
        except OSError:
            os.mkdir(self.PATH_LOOT)
            self.download_file(args)

class DownloadFileCommand(Command):

    def __init__(self, receiver):
        self.receiver = receiver

    
    def execute(self, args):
        self.receiver.download_file(args)


