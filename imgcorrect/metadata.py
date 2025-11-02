"""Copy and modify image metadata."""

import logging
import subprocess
from concurrent.futures import ThreadPoolExecutor

from imgparse import MetadataParser

logger = logging.getLogger(__name__)


def copy_exif_parallel_apply(image_df, exiftool_path, max_workers):
    """Copy EXIF metadata in parallel with progress bar."""
    executor = ThreadPoolExecutor(max_workers=max_workers)
    futures = {}
    
    for idx, (_, row) in enumerate(image_df.iterrows()):
        future = executor.submit(copy_exif, row, exiftool_path)
        futures[idx] = future
    
    def _wait_for_result(row):
        idx = row.name if hasattr(row, 'name') else 0
        if idx in futures:
            futures[idx].result()
        return row
    
    image_df.progress_apply(_wait_for_result, axis=1)
    executor.shutdown()


def copy_exif(image_df_row, exiftool_path):
    """Copy image metadata with necessary changes from original image to corrected image."""
    command = [
        exiftool_path,
        "-config",
        "cfg/exiftool.cfg",
        "-overwrite_original",
        "-TagsFromFile",
        image_df_row.image_path,
        "-all",
        "--xmp-Camera:ColorTransform",
        "--xmp-Camera:SunSensor",
        "-xmp-Camera:IsNormalized=1",
        "-xmp-Camera:BlackCurrent=",
        "-xmp-Camera:BlackCurrent=0",
    ]
    if image_df_row.reduce_xmp:
        parser = MetadataParser(image_df_row.image_path)
        cent_arr, fwhm_arr = parser.wavelength_data()
        band_arr = parser.bandnames()
        i = int(image_df_row.XMP_index)
        command += [
            "-xmp-Camera:BandName=",
            "-xmp-Camera:CentralWavelength=",
            "-xmp-Camera:WavelengthFWHM=",
            f"-xmp-Camera:BandName={band_arr[i]}",
            f"-xmp-Camera:CentralWavelength={cent_arr[i]}",
            f"-xmp-Camera:WavelengthFWHM={fwhm_arr[i]}",
        ]
    command.append(image_df_row.temp_path)

    # Use CREATE_NO_WINDOW flag on Windows if available (Python 3.7+)
    kwargs = {"capture_output": True}
    if hasattr(subprocess, "CREATE_NO_WINDOW"):
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

    # Simple retry mechanism (3 attempts)
    for attempt in range(3):
        results = subprocess.run(command, **kwargs)
        if results.returncode == 0:
            break
        if attempt < 2:  # Not the last attempt
            logger.warning(f"Exiftool retry {attempt + 1}/3 for {image_df_row.temp_path}")
        else:
            raise ValueError(f"Exiftool failed for {image_df_row.temp_path}: {results.stderr.decode('utf-8', errors='ignore') if results.stderr else 'unknown error'}")
