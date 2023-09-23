#!/usr/bin/env python3
# encoding: utf-8
# Copyright 2022 Huawei Technologies Co., Ltd.All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Setup."""

import sys
import os
import shutil
import stat
import platform
import shlex
import subprocess
from importlib import import_module
from setuptools import setup, find_packages
from setuptools.command.egg_info import egg_info
from setuptools.command.build_py import build_py
from setuptools.command.install import install


def get_configs_content():
    pwd = os.path.dirname(os.path.realpath(__file__))
    configs = [os.path.join(root, file)
               for root, _, file_list in os.walk(os.path.join(pwd, "configs")) for file in file_list
               if file.endswith('.yaml') or file.endswith(".yml") or file.endswith(".md")]
    return configs


def get_readme_content():
    pwd = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(pwd, 'README.md'), encoding='UTF-8') as f:
        return f.read()


def get_platform():
    """
    Get platform name.

    Returns:
        str, platform name in lowercase.
    """
    return platform.system().strip().lower()


def get_description():
    """
    Get description.

    Returns:
        str, wheel package description.
    """
    os_info = get_platform()
    cpu_info = platform.machine().strip()

    cmd = "git log --format='[sha1]:%h, [branch]:%d' -1"
    process = subprocess.Popen(
        shlex.split(cmd),
        shell=False,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, _ = process.communicate()
    if not process.returncode:
        git_version = stdout.decode().strip()
        return 'mindformers platform: %s, cpu: %s, git version: %s' % (os_info, cpu_info, git_version)

    return 'mindformers platform: %s, cpu: %s' % (os_info, cpu_info)


def get_install_requires():
    """
    Get install requirements.

    Returns:
        list, list of dependent packages.
    """
    with open('requirements.txt') as file:
        return file.read().strip().splitlines()


def update_permissions(path):
    """
    Update permissions.

    Args:
        path (str): Target directory path.
    """
    for dirpath, dirnames, filenames in os.walk(path):
        for dirname in dirnames:
            dir_fullpath = os.path.join(dirpath, dirname)
            os.chmod(dir_fullpath, stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC | stat.S_IRGRP | stat.S_IXGRP)
        for filename in filenames:
            file_fullpath = os.path.join(dirpath, filename)
            os.chmod(file_fullpath, stat.S_IREAD)


class EggInfo(egg_info):
    """Egg info."""

    def run(self):
        egg_info_dir = os.path.join(os.path.dirname(__file__), 'mindformers.egg-info')
        shutil.rmtree(egg_info_dir, ignore_errors=True)
        super().run()
        update_permissions(egg_info_dir)


class BuildPy(build_py):
    """Build py files."""

    def run(self):
        mindspore_transformer_lib_dir = os.path.join(os.path.dirname(__file__), 'build', 'lib', 'mindformers')
        shutil.rmtree(mindspore_transformer_lib_dir, ignore_errors=True)
        super().run()
        update_permissions(mindspore_transformer_lib_dir)


class Install(install):
    """Install."""

    def run(self):
        super().run()
        if sys.argv[-1] == 'install':
            pip = import_module('pip')
            mindspore_transformer_dir = os.path.join(os.path.dirname(pip.__path__[0]), 'mindformers')
            update_permissions(mindspore_transformer_dir)


if __name__ == '__main__':
    version_info = sys.version_info
    if (version_info.major, version_info.minor) < (3, 7):
        sys.stderr.write('Python version should be at least 3.7\r\n')
        sys.exit(1)

    setup(
        name='mindformers',
        version='0.3.0',
        author='The MindSpore Authors',
        author_email='contact@mindspore.cn',
        url='https://www.mindspore.cn',
        download_url='https://gitee.com/mindspore/mindformers/tags',
        project_urls={
            'Sources': 'https://gitee.com/mindspore/mindformers',
            'Issue Tracker': 'https://gitee.com/mindspore/mindformers/issues',
        },
        description=get_description(),
        long_description=get_readme_content(),
        long_description_content_type="text/markdown",
        test_suite="tests",
        packages=find_packages(exclude=["*tests*"]),
        platforms=[get_platform()],
        include_package_data=True,
        package_data={'mindformers': get_configs_content()},
        cmdclass={
            'egg_info': EggInfo,
            'build_py': BuildPy,
            'install': Install,
        },
        python_requires='>=3.7',
        install_requires=get_install_requires(),
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Console',
            'Environment :: Web Environment',
            'Intended Audience :: Science/Research',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: Apache Software License',
            'Programming Language :: Python :: 3 :: Only',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Topic :: Scientific/Engineering',
            'Topic :: Scientific/Engineering :: Artificial Intelligence',
            'Topic :: Software Development',
            'Topic :: Software Development :: Libraries',
            'Topic :: Software Development :: Libraries :: Python Modules',
        ],
        license='Apache 2.0',
        keywords='mindformers',
    )
