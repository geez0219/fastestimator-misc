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
from glob import glob
from pathlib import Path
from typing import Optional

import pandas as pd
import wget

from fastestimator.dataset.csv_dataset import CSVDataset
from fastestimator.util.wget_util import bar_custom, callback_progress

wget.callback_progress = callback_progress


def load_data(root_dir: Optional[str] = None) -> CSVDataset:
    """
    Download the montgomery dataset to local storage if not already downloaded.
    Sourced from: http://openi.nlm.nih.gov/imgs/collections/NLM-MontgomeryCXRSet.zip
    Args:
        root_dir: The path to store the USPS data. If not provided then data is saved to `fastestimator_data` in the
                  users home directory
    Returns:
        TrainData
    """
    home = str(Path.home())

    if root_dir is None:
        root_dir = os.path.join(home, 'fastestimator_data', 'Montgomery')
    else:
        root_dir = os.path.join(os.path.abspath(root_dir), 'Montgomery')
    os.makedirs(root_dir, exist_ok=True)

    csv_path = os.path.join(root_dir, "montgomery.csv")
    data_compressed_path = os.path.join(root_dir, 'NLM-MontgomeryCXRSet.zip')
    extract_folder_path = os.path.join(root_dir, 'MontgomerySet')

    if not os.path.exists(extract_folder_path):
        # download
        if not os.path.exists(data_compressed_path):
            print("Downloading data to {}".format(root_dir))
            wget.download(
                'http://openi.nlm.nih.gov/imgs/collections/NLM-MontgomeryCXRSet.zip',
                root_dir,
                bar=bar_custom)

        # extract
        print("\nExtracting file ...")
        with zipfile.ZipFile(data_compressed_path, 'r') as zip_file:
            # There's some garbage data from macOS in the zip file that gets filtered out here
            zip_file.extractall(
                root_dir,
                filter(lambda x: x.startswith("MontgomerySet/"),
                       zip_file.namelist()))

    # smaple the dataset
    data_subsample(os.path.join(extract_folder_path, "CXR_png"), 20)

    # glob and generate csv
    if not os.path.exists(csv_path):
        img_list = glob(os.path.join(extract_folder_path, 'CXR_png', '*.png'))
        df = pd.DataFrame(data={'image': img_list})
        df['image'] = df['image'].apply(lambda x: os.path.relpath(x, root_dir))
        df['image'] = df['image'].apply(os.path.normpath)
        df['mask_left'] = df['image'].str.replace(
            'CXR_png', os.path.join('ManualMask', 'leftMask'))
        df['mask_right'] = df['image'].str.replace(
            'CXR_png', os.path.join('ManualMask', 'rightMask'))
        df.to_csv(csv_path, index=False)

    return CSVDataset(csv_path)



def data_subsample(source_dir, sample_num):
    # subsample the image
    img_count = 0
    for dirpath, _, filenames in os.walk(source_dir):
        for f in filenames:
            if img_count < sample_num:
                img_count += 1
            else:
                os.remove(os.path.join(dirpath, f))

if __name__ == "__main__":
    load_data()