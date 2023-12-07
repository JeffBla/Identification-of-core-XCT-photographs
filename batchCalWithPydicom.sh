dataDirHead="dcmCutCycleOut_resnet_clip/train/"

dataDirAT_1_3="AT-1_3(1~98.5m)"
dataDirAT_1_15="AT-1_15(2~99.4m_export-2)"
dataDirAT_1_20="AT-1_20(1.1~98.6m)"
dataDirAT_1_69="AT-1_69(1.3~98.8m)"
dataDirAT_1_76="AT-1_76(1.2~98.2m_export-2)"
dataDirAT_1_86="AT-1_86(1.7~98.1m)"
dataDirAT_1_92="AT-1_92(1.6~98.6m_export-2)"
dataDirAT_1_99="AT-1_99(1.4~98.9m_export-2)"
dataDirBH_3_3="BH-3_3(1~98.8m)"
dataDirBH_3_15="BH-3_15(1~98.8m_export-2)"
dataDirBH_3_19="BH-3_19(1~98.6m)"

ctAT_1_3="845.375"
ctAT_1_15="720.375"
ctAT_1_20="1595.375"
ctAT_1_69="1595.375"
ctAT_1_76="1720.375"
ctAT_1_86="1470.375"
ctAT_1_92="1345.375"
ctAT_1_99="1720.375"
ctBH_3_3="1220.375"
ctBH_3_15="1095.375"
ctBH_3_19="1595.375"

outDirHead="./projectDEMO/resnet_pred/"
outputPrefix="traditionalCalWithPydicom_"

dataDirArr=($dataDirAT_1_3 $dataDirAT_1_15 $dataDirAT_1_20 $dataDirAT_1_69
    $dataDirAT_1_76 $dataDirAT_1_86 $dataDirAT_1_92 $dataDirAT_1_99
    $dataDirBH_3_3 $dataDirBH_3_15 $dataDirBH_3_19)

ctArr=($ctAT_1_3 $ctAT_1_15 $ctAT_1_20 $ctAT_1_69
    $ctAT_1_76 $ctAT_1_86 $ctAT_1_92 $ctAT_1_99
    $ctBH_3_3 $ctBH_3_15 $ctBH_3_19)

len=${#dataDirArr[@]}

# put the result together -> train and test
for ((i=0; i < len; i++)); do
    python readDicomCntCT_findPorosityByPydicom_contour.py \
        "$dataDirHead${dataDirArr[$i]}" \
        "--CTG" \
        "${ctArr[$i]}" \
        "--csv_output" \
        "$outDirHead$outputPrefix${ctArr[$i]}"_"${dataDirArr[$i]}".csv
done