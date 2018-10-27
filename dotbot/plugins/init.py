import os
import glob
import shutil
import dotbot
import subprocess
from argparse import ArgumentParser
from dotbot.config import ConfigReader, ReadingError
from dotbot.cli import add_options, read_config


class Init(dotbot.Plugin):
    '''
    Populate with dotfiles.
    '''

    _directive = 'init'

    def can_handle(self, directive):
        return directive == self._directive

    def handle(self, directive, data):
        if directive != self._directive:
            raise ValueError('Init cannot handle directive %s' % directive)
        data = self._get_links()
        return self._process_links(data)

    def _process_links(self, links):
        success = True
        for source, destination in links.items():
            relative = False
            source = os.path.expanduser(source)
            if self._is_link(source):
                continue
            destination = self._default_source(source, destination)
            if os.path.isfile(source):
                path = '/'.join(source.split('/')[:-1])
                path = '/'.join(path.split('/')[3:])
                if path.startswith('.'):
                    path = path[1:]
                if not os.path.exists(path):
                    os.makedirs(path)
            success &= self._copy(source, destination, relative)
        if success:
            print('All dotfiles have been initialized')
        else:
            print('Some dotfiles were not successfully initialized')
        return success

    def _copy(self, source, destination, relative):
        print(source)
        print(destination)
        if os.path.isfile(source):
            shutil.copy2(source, destination)
        elif os.path.isdir(source):
            shutil.copytree(source, destination)
        print('Copying %s -> %s' % (source, destination))
        return True

    def _default_source(self, source, destination):
        if destination is None:
            basename = source
            if source.startswith('/home/'):
                basename = '/'.join(source.split('/')[3:])
            if basename.startswith('.'):
                return basename[1:]
            else:
                return basename
        else:
            return source

    def _get_links(self):
        parser = ArgumentParser()
        add_options(parser)
        options = parser.parse_args()
        tasks = read_config(options.config_file)
        data = []
        for task in tasks:
            k = next(iter(task))
            if k == 'link':
                data = task['link']
        return data

    def _is_link(self, path):
        '''
        Returns true if the path is a symbolic link.
        '''
        return os.path.islink(os.path.expanduser(path))
