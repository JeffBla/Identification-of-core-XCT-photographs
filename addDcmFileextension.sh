prefix='/home/jeffbla/resourceDPProject/bh-3 DICOM-20230421T075124Z-001/bh-3 DICOM/bh_3_'

target='20/13420001'

cd "${prefix}${target}"
mkdir ../13420001_dcm

for file in $(ls '.'); do
    cp $file "${prefix}${target}_dcm/${file}.dcm"
done
