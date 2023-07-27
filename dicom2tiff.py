import dicom2jpg
from pathlib import Path

dicom_dir = Path(
    "./bh-3 DICOM-20230421T075124Z-001/bh-3 DICOM/bh_3_18/13300001_dcm")
export_location = Path("./bh-3 DICOM-20230421T075124Z-001/BmpOut/16/000")

dicom2jpg.dicom2jpg(dicom_dir, target_root=export_location)
