# Copyright 2019 The FastEstimator Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

import os
import zipfile
from pathlib import Path
from typing import Optional, Tuple

import wget

from fastestimator.dataset.siamese_dir_dataset import SiameseDirDataset
from fastestimator.util.wget_util import bar_custom, callback_progress

wget.callback_progress = callback_progress


def load_data(
    root_dir: Optional[str] = None
) -> Tuple[SiameseDirDataset, SiameseDirDataset]:
    """Download the Omniglot dataset to local storage.
    Args:
        root_dir: The path to store the  data. When `path` is not provided, will save at
            `fastestimator_data` under user's home directory.
    Returns:
        TrainData, EvalData
    """
    if root_dir is None:
        root_dir = os.path.join(str(Path.home()), 'fastestimator_data',
                                'Omniglot')
    else:
        root_dir = os.path.join(os.path.abspath(root_dir), 'Omniglot')
    os.makedirs(root_dir, exist_ok=True)

    train_path = os.path.join(root_dir, 'images_background')
    eval_path = os.path.join(root_dir, 'images_evaluation')
    train_zip = os.path.join(root_dir, 'images_background.zip')
    eval_zip = os.path.join(root_dir, 'images_evaluation.zip')

    files = [
        (train_path, train_zip,
         'https://github.com/brendenlake/omniglot/raw/master/python/images_background.zip'
         ),
        (eval_path, eval_zip,
         'https://github.com/brendenlake/omniglot/raw/master/python/images_evaluation.zip'
         )
    ]

    for data_path, data_zip, download_link in files:
        if not os.path.exists(data_path):
            # Download
            if not os.path.exists(data_zip):
                print("Downloading data: {}".format(data_zip))
                wget.download(download_link, data_zip, bar=bar_custom)
            # Extract
            print("Extracting data: {}".format(data_path))
            with zipfile.ZipFile(data_zip, 'r') as zip_file:
                zip_file.extractall(root_dir)

    data_subsample(train_path, sample_num_per_class=3)
    data_subsample(eval_path, sample_num_per_class=3)

    return SiameseDirDataset(train_path), SiameseDirDataset(eval_path)


def data_subsample(source_dir, sample_num_per_class):
    # subsample the image
    for dirpath, _, filenames in os.walk(source_dir):
        img_count = 0
        for f in filenames:
            if img_count < sample_num_per_class:
                img_count += 1
            else:
                os.remove(os.path.join(dirpath, f))

if __name__ == "__main__":
    load_data()