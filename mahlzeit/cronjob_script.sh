#!/usr/bin/env bash
# */10 * * * * /home/frevilla/devel/scrapy/mahlzeit/mahlzeit/cronjob_script.sh
set -x

print_command_output()
{
if [ $? -eq 0 ]; then
    echo "OK" >> /tmp/mybackup.log
else
    echo "FAIL" >> /tmp/mybackup.log
fi
}

run_server_deploy()
{
DEPLOY_SCRIPT=/home/frevilla/devel/culinarius/prepare_deploy_script.sh
/bin/sh ${DEPLOY_SCRIPT}
}


echo "######### START RUNNING SCRIPT $(date) ##########" >> /tmp/mybackup.log
#PATH=$PATH:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/frevilla/.local/bin/scrapy
PATH=/home/frevilla/bin:/home/frevilla/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin
export PATH
cd /home/frevilla/devel/scrapy/mahlzeit/
/home/frevilla/.local/bin/scrapy coolinarius --backup --run --force-deploy
print_command_output
echo "######### STOP RUNNING SCRIPT $(date) ##########" >> /tmp/mybackup.log


