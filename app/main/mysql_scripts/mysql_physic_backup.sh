#!/bin/bash

ulimit -n 65536

### Usage will be helpful when you need to input the valid arguments

function get_key_value()
{
    echo "$1" | sed 's/^--[a-zA-Z_-]*=//'
}

function usage(){
  cat << EOF
  Usage:$0 [configure-options]
  -?,--help		 Show this help message
  --backup-dir=<>	 Set backup directory
  --defaults-file=[]	 Set mysql configuration file
  --host=<>		 Set mysql host
  --port=<>		 Set mysql port
  --user=<>		 set mysql username
  --socket=<>		 set mysql Socket
EOF
}


if test $# -eq 0 ; then
  usage
  exit 0;
fi

function parse_options()
{
  while test $# -gt 0
  do
    case "$1" in
    --backup-dir=*)
      backup_dir=`get_key_value "$1"` ;;
    --defaults-file=*)
      defaults_file=`get_key_value "$1"` ;;
    --host=*)
      host=`get_key_value "$1"` ;;
    --port=*)
      port=`get_key_value "$1"` ;;
    --user=*)
      user=`get_key_value "$1"` ;;
    --socket=*)
      socket=`get_key_value "$1"` ;;
    -? | --help )
      usage
      exit 0;;
    *)
      echo "UnKnown option '$1' "
      exit 1;;
    esac
    shift
  done

}

parse_options "$@"

day=`date +%w`
ts=`date +%Y%m%d%H%M%S`
logfile=$backup_dir/full_log_$ts.log
## add 2017-09-28 ##
base_dir=`basename $backup_dir`
##########################
fulldir=`hostname`_full_$ts
expired_time=0

if [ ! -d "$backup_dir" ]; then
  echo " backup_dir does not exists!" >> $logfile
  sudo mkdir -p $backup_dir/`hostname`_tar_backup
fi

if [ ! -d "$backup_dir/`hostname`_tar_backup" ]; then
  echo " backup_dir does not exists!" >> $logfile
  sudo mkdir -p $backup_dir/`hostname`_tar_backup
fi

if [ -z "`mysqladmin --user=$user --password=test --port=$port --host=$host status | grep 'Uptime' `" ]; then
  echo "MySQL is not Running " >> $logfile
fi

if [  -z "$defaults_file" ]; then
  echo "defaults-file is not defined, used defaults-file=/etc/my.cnf " >> $logfile
  defaults_file="/etc/my.cnf"
fi


echo "Start InnoBackup at `date` ." >> $logfile
echo "Current defaults file = $defaults_file " >> $logfile
echo "Current host = $host " >> $logfile
echo "Current user = $user " >> $logfile
echo "Current port = $port " >> $logfile
echo "Current socket = $socket " >> $logfile
echo "Current logfile = $logfile " >> $logfile

function backup_full()
{
  sudo innobackupex --defaults-file=$defaults_file --user=$user --password=test --port=$port --host=$host --socket=$socket --parallel=8 --no-timestamp --slave-info $backup_dir/$fulldir 2>> $logfile
  status=$?
  if [ $status -eq 0 ]; then
    echo "backup_full is successfull complete !" >>$logfile
  else
    exit
  fi
}

function apply_log()
{
  cd $backup_dir/$fulldir
  sudo innobackupex --apply-log ./ 2>>$logfile
  status=$?
  if [ $status -eq 0 ]; then
    echo "apply_log is successfull complete !" >>$logfile
  else
    exit
  fi
}

function compress_backup()
{
  cd  $backup_dir/$fulldir
  sudo tar -zcvf $backup_dir/`hostname`_tar_backup/$fulldir.tar.gz ./ >>$logfile
  status=$?
  if [ $status -eq 0 ]; then
    echo "compress_backup is successfull complete !" >>$logfile
  else
    exit
  fi
}

function remove_expired_backup()
{
  # add -prune param, fixed print No Such File or directory
  #sudo find $backup_dir -name "*full_*" -mtime +$expired_time -exec rm -rf {} \; -prune
  find $backup_dir -name '*full_*' |xargs rm -rf ;
  status=$?
  if [ $status -eq 0 ]; then
    echo "remove_expired_backup is successfull complete !" >>$logfile
  else
    exit
  fi
}

function grant_privileges(){
  `chown -R mysql:mysql $backup_dir/$fulldir`
}

function start_mysql(){
  sudo mysqld_safe \
  --no-defaults \
  --basedir=/usr \
  --datadir=$backup_dir/$fulldir \
  --log-error=$backup_dir/$fulldir/error.log \
  --open-files-limit=65535 \
  --pid-file=$backup_dir/$fulldir/mysqld.pid \
  --socket=$backup_dir/$fulldir/mysqld.sock \
  --port=10000 \
  --user=mysql >> $logfile &
  printf "\n"

  if [ $? -eq 0 ] ;then
    printf "start mysql complete !!! \n"
  else
    printf "start mysql failure !!! \n"
    exit 1
  fi
}

function visit_mysql(){
  mysqladmin -utest -ptest -h127.0.0.1 -P10000 ping >> $logfile 2>&1
  if [ $? -eq 0 ] ;then
    printf "mysqld is alived !!! \n"
  else
    printf "mysqld is not running !!! \n"
    exit 1
  fi
}

function stop_mysql(){
  mysqladmin -utest -ptest -h127.0.0.1 -P10000 shutdown >> $logfile 2>&1
  if [ $? -eq 0 ] ;then
    printf "mysqld stopped succuess !!! \n"
  else
    printf "mysqld stop failed !!! \n"
    exit 1
  fi
}

function rsync_to_remote_server(){
  rsync -avz $backup_dir/`hostname`_tar_backup mysql@10.1.1.20::mysql_product_bak/$base_dir --password-file=/etc/rsyncd/rsyncd.pass >> $logfile 2>&1
  if [ $? -eq 0 ] ;then
    printf "rsync succuess !!! \n"
  else
    printf "rsync failed !!! \n"
    exit 1
  fi
}

#case $day in
#   6)
#Sunday Full backup
	remove_expired_backup
	backup_full
	apply_log
	grant_privileges
	start_mysql
	sleep 60
	visit_mysql
	stop_mysql
	sleep 60
	compress_backup	
	rsync_to_remote_server
#        ;;
#esac
ts_end=`date +%Y%m%d%H%M%S`

if [ -e "$logfile" ];then
  status=`grep -in 'completed OK!' $logfile | grep -v 'prints "completed OK!"' | wc -l`
  if test $status -eq 2 ; then
    python $backup_dir/sendbackup_info.py "admin" "succuess full backup for MySQL ON `hostname` start_at:$ts end_in:  $ts_end and verify the backup can be recovery !"
  else
    python $backup_dir/sendbackup_info.py "admin" "failed full backup for MySQL ON `hostname` start_at:$ts  end_in: $ts_end "
  fi
fi

exit



