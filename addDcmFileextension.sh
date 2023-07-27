cd '/home/jeffbla/resourceDPProject/bh-3 DICOM-20230421T075124Z-001/bh-3 DICOM/bh_3_18/13300001'
mkdir ../13300001_dcm

for file in $(ls '.')
do
    cp $file "/home/jeffbla/resourceDPProject/bh-3 DICOM-20230421T075124Z-001/bh-3 DICOM/bh_3_18/13300001_dcm/${file}.dcm"
done