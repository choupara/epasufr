workspace=$(pwd)
log_dir="$workspace/../log"
input_dir="$workspace/../input_instance"
date_time=$(date +'%d-%m-%Y_%H-%M-%S')
log_file="$log_dir/bench_$date_time.log"
touch $log_file
for files in $input_dir/*.lp; do
    echo "Processing file: $files" | tee -a $log_file        
    echo -e "3\nn" | python interp_proj_fasb.py $files | tee -a $log_file
    echo "Finished processing file: $files" | tee -a $log_file
    echo "----------------------------------------" | tee -a $log_file
done


