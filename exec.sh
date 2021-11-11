myloc=$(realpath "$0" | sed 's|\(.*\)/.*|\1|')
dirLogs='/home/omia/Documents/logs'
source  $myloc/env/bin/activate
python3  $myloc/status.py -n QS --logFlujoFaust $dirLogs/flujo/faust.log --logFlujoDs $dirLogs/flujo/ds.log --logAforoFaust $dirLogs/aforo/faust.log --logAforoDs $dirLogs/aforo/ds.log
