dcmDirHead="CTimageWithPorosity/"

dcmDirAT_1_3_1="AT-1_3_1"
dcmDirAT_1_3_2="AT-1_3_2"
dcmDirAT_1_3_3="AT-1_3_3"
dcmDirAT_1_15_1="AT-1_15_1"
dcmDirAT_1_20_1="AT-1_20_1"
dcmDirAT_1_20_2="AT-1_20_2"
dcmDirAT_1_69_1="AT-1_69_1"
dcmDirAT_1_69_2="AT-1_69_2"
dcmDirAT_1_76_1="AT-1_76_1"
dcmDirAT_1_86_1="AT-1_86_1"
dcmDirAT_1_86_2="AT-1_86_2"
dcmDirAT_1_92_1="AT-1_92_1"
dcmDirAT_1_99_1="AT-1_99_1"
dcmDirBH_3_3_1="BH-3_3_1"
dcmDirBH_3_3_2="BH-3_3_2"
dcmDirBH_3_15_1="BH-3_15_1"
dcmDirBH_3_19_1="BH-3_19_1"
dcmDirBH_3_19_2="BH-3_19_2"

dcmDirArr_train=($dcmDirAT_1_3_2 $dcmDirAT_1_3_3 $dcmDirAT_1_15_1 $dcmDirAT_1_20_1
    $dcmDirAT_1_20_2 $dcmDirAT_1_69_1 $dcmDirAT_1_69_2 $dcmDirAT_1_76_1
    $dcmDirAT_1_86_1 $dcmDirAT_1_86_2 $dcmDirAT_1_92_1 $dcmDirAT_1_99_1)

dcmDirArr_test=($dcmDirAT_1_3_1 $dcmDirBH_3_19_2 $dcmDirBH_3_19_1
    $dcmDirBH_3_15_1 $dcmDirBH_3_3_2 $dcmDirBH_3_3_1)

# put the result separately
# target=16
# cnt=0
# for dcmDir in ${dcmDirArr[@]}; do
#     if [ $cnt -eq 2 ]; then
#         cnt=0
#         ((target++))
#     fi
#     python readDicom_removeContainer_withErode.py \
#         "$dcmDirHead$dcmDir" \
#         -outDirname "./dcmCutCycleOut/$target" \
#         --isTwice
#     ((cnt++))
# done

# put the result together -> train and test
for dcmDir in ${dcmDirArr_train[@]}; do
    mkdir  "./dcmCutCycleOut/train/$dcmDir"
    python readDicom_removeContainer_withErode.py \
        "$dcmDirHead$dcmDir" \
        -outDirname "./dcmCutCycleOut/train/$dcmDir" \
        --isTwice
done

for dcmDir in ${dcmDirArr_test[@]}; do
    mkdir  "./dcmCutCycleOut/test/$dcmDir"
    python readDicom_removeContainer_withErode.py \
        "$dcmDirHead$dcmDir" \
        -outDirname "./dcmCutCycleOut/test/$dcmDir" \
        --isTwice
done
