#!/usr/bin/env bash
# */10 * * * Wed sh /home/frevilla/devel/scrapy/mahlzeit/mahlzeit/cronjob_script.sh
# 0 9,23 * * Mon sh /home/frevilla/devel/scrapy/mahlzeit/mahlzeit/cronjob_script.sh
set -x

TIMESTAMP="$(date +%Y-%m-%d-%H:%M:%S)"
LOG=/tmp/coolinarius_job.log
DEPLOY_SCRIPT=/home/frevilla/devel/github/culinarius/prepare_deploy_script.sh
DIR=/home/frevilla/devel/github/mahlzeit/

print_command_output()
{
if [ $? -eq 0 ]; then
    echo "[COOLINARIUS ${TIMESTAMP}] OK" >> ${LOG}
else
    echo "[COOLINARIUS ${TIMESTAMP}] FAIL" >> ${LOG}
fi
}

run_server_deploy()
{
/bin/sh ${DEPLOY_SCRIPT}
}


echo "######### START RUNNING SCRIPT ${TIMESTAMP} ##########" >> ${LOG}
# set path
PATH=/home/frevilla/bin:/home/frevilla/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin
export PATH
# execute command
cd ${DIR}
/home/frevilla/.local/bin/scrapy coolinarius --backup --run --force-deploy
# log output
print_command_output
echo "######### STOP RUNNING SCRIPT ${TIMESTAMP} ##########" >> ${LOG}
