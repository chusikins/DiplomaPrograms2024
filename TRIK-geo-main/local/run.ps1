# $pi_ip = '192.168.30.30'
# $pi_user='pi'
# $pi_password='raspberry'
# $working_dir_pi='/home/pi/aleks'
$pi_ip = '10.0.0.31'
$pi_user='ubuntu'
$pi_password='geoscan123'
$working_dir_pi='/home/ubuntu/roboticsPractice2023'


$working_dir_windows='C:\Users\aleks\PycharmProjects\TRIK-geo'


# process flight and recordings
plink -ssh $pi_user@$pi_ip -pw $pi_password -m local\create_dirs_pi.sh
pscp -pw $pi_password drone\geo_flight.py $pi_user@${pi_ip}:${working_dir_pi}
plink -ssh $pi_user@$pi_ip -pw $pi_password -m $working_dir_windows\drone\run_python_pi.sh

# download frams to local machine
rm $working_dir_windows\data\frames\*
pscp -pw $pi_password $pi_user@${pi_ip}:${working_dir_pi}/aleks/frames/* $working_dir_windows\data\frames

# make pano
# python local\capture.py

