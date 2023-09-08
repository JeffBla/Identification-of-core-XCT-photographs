dcmDirHead="bh-3 DICOM-20230421T075124Z-001/bh-3 DICOM/bh_3_"

dcmDir16_1="16/13170000_dcm"
dcmDir16_2="16/13170001_dcm"
dcmDir17_1="17/13240000_dcm"
dcmDir17_2="17/13240001_dcm"
dcmDir18_1="18/13300000_dcm"
dcmDir18_2="18/13300001_dcm"
dcmDir19_1="19/13360000_dcm"
dcmDir19_2="19/13360001_dcm"
dcmDir20_1="20/13420000_dcm"
dcmDir20_2="20/13420001_dcm"

dcmDirArr=($dcmDir16_1 $dcmDir16_2 $dcmDir17_1 $dcmDir17_2
    $dcmDir18_1 $dcmDir18_2 $dcmDir19_1 $dcmDir19_2
    $dcmDir20_1 $dcmDir20_2)

target=16
cnt=0
for dcmDir in ${dcmDirArr[@]}; do
    if [ $cnt -eq 2 ]; then
        cnt=0
        ((target++))
    fi
    python readDicom_removeContainer_withErode.py \
        "$dcmDirHead$dcmDir" \
        -outDirname "./dcmCutCycleOut/$target"
    ((cnt++))
done
