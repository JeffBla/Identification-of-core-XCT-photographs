prefix='/home/chen_yi/resourceDPProject/bh-3 DICOM-20230421T075124Z-001/bh-3 DICOM/bh_3_15'

target='/13490000'

cd "${prefix}${target}"
mkdir ../13490000_dcm

for file in $(ls '.'); do
    cp $file "${prefix}${target}_dcm/${file}.dcm"
done
