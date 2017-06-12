#!/bin/bash
set -e

. docker-java-home

#echo "\$1=$1 UID=$UID GID=$GID whoami=`whoami` id=`id` \$@=$@"

# allow the container to be started with `--user`
if [ "$1" = 'bin/start-bamboo.sh' -a "$(id -u)" = '0' ]; then
    if [ ! -f $BAMBOO_INST/conf/server.xml ]; then /configure; fi
    chown -R $UID:$UID $BAMBOO_INST
    chown -R $UID:$GID $BAMBOO_HOME
    exec gosu $UID "$BASH_SOURCE" "$@"
fi

exec "$@"