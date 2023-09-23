# Copyright 2022 Huawei Technologies Co., Ltd
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
# ============================================================================
'''download_tools'''
import time
import os
import requests
import urllib3

from tqdm import tqdm

from mindformers.tools.logger import logger
try:
    import fcntl
except ImportError:
    fcntl = None
    logger.warning("The library fcntl is not found. This may cause the reading file failed "
                   "when call the from_pretrained for different process.")

urllib3.disable_warnings()

class StatusCode:
    '''StatusCode'''
    succeed = 200


def download_with_progress_bar(url, filepath, chunk_size=1024, timeout=4):
    '''download_with_progress_bar'''
    if not os.path.exists(filepath):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

    header = {
        "Accept-Encoding": "identity",
        "User-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:65.0) Gecko/20100101 Firefox/65.0'
    }

    start = time.time()

    try:
        response = requests.get(url, verify=False, stream=True, timeout=timeout)
    except (TimeoutError, urllib3.exceptions.MaxRetryError,
            requests.exceptions.ProxyError,
            requests.exceptions.ConnectionError):
        logger.error("Connect error, please download %s to %s.", url, filepath)
        return False

    content_size = response.headers.get('content-length')

    if content_size is None:
        response_json = response.json()
        download_url = response_json.get("data").get("download_url")
        if download_url:
            response = requests.get(download_url, verify=False, stream=True, timeout=timeout, headers=header)
            content_size = int(response.headers.get('content-length'))
        else:
            logger.error("Download url parsing failed from json file, please download %s to %s.", url, filepath)
            return False
    else:
        content_size = int(content_size)

    size = 0
    if response.status_code == StatusCode.succeed:
        logger.info('Start download %s', filepath)
        with open(filepath, 'wb') as file:
            if fcntl:
                fcntl.flock(file.fileno(), fcntl.LOCK_EX)

            with tqdm(total=content_size, desc='Downloading',
                      leave=True, ncols=100, unit='B', unit_scale=True) as pbar:
                for data in response.iter_content(chunk_size=chunk_size):
                    file.write(data)
                    size += len(data)
                    pbar.update(1024)
        end = time.time()
        logger.info('Download completed!,times: %.2fs', (end - start))
        return True

    logger.error("%s is unconnected!", url)
    return False
