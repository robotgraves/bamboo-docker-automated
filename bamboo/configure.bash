#!/bin/bash
set -e

. /usr/local/share/atlassian/common.sh

configureContainerDS() {
  cp ${BAMBOO_INST}/conf/server.xml ${BAMBOO_INST}/conf/server-backup.xml
  xmlstarlet ed -a "//Server/Service/Engine/Host/Context/Manager" --type elem -n "Resource name=\"jdbc/$JNDI_DATASOURCE\"
        auth=\"Container\"
        type=\"javax.sql.DataSource\"
        username=\"$DB_USER\"
        password=\"$DB_PASSWORD\"
        driverClassName=\"$DB_JDBC_DRIVER\"
        url=\"$DB_JDBC_URL\"
        maxActive=\"100\"
        maxIdle=\"7\"
        validationQuery=\"Select 1\"" -v "" ${BAMBOO_INST}/conf/server-backup.xml > ${BAMBOO_INST}/conf/server.xml

  cp ${BAMBOO_INST}/atlassian-bamboo/WEB-INF/web.xml ${BAMBOO_INST}/atlassian-bamboo/WEB-INF/web-backup.xml
  xmlstarlet ed -N x="http://java.sun.com/xml/ns/javaee" -a "//_:error-page[last()]" --type elem -n 'resource-ref' -v "" ${BAMBOO_INST}/atlassian-bamboo/WEB-INF/web-backup.xml |
  xmlstarlet ed -N x="http://java.sun.com/xml/ns/javaee" --subnode '//_:resource-ref[last()]' --type elem -n "description" -v "Connection Pool" \
        --subnode '//_:resource-ref[last()]' --type elem -n "res-ref-name" -v "jdbc/$JNDI_DATASOURCE" \
        --subnode '//_:resource-ref[last()]' --type elem -n "res-type" -v "javax.sql.DataSource" \
        --subnode '//_:resource-ref[last()]' --type elem -n "res-auth" -v "Container" > ${BAMBOO_INST}/atlassian-bamboo/WEB-INF/web.xml
}
if [ "$CONTEXT_PATH" == "ROOT" -o -z "$CONTEXT_PATH" ]; then
    CONTEXT_PATH=
else
    CONTEXT_PATH="/$CONTEXT_PATH";
fi
xmlstarlet ed -u '//Context/@path' -v "$CONTEXT_PATH" $BAMBOO_INST/conf/server-backup.xml > $BAMBOO_INST/conf/server.xml
if [ -n "$DATABASE_URL" ]; then
  extract_database_url "$DATABASE_URL" DB ${BAMBOO_INST}/lib
  DB_JDBC_URL="$(xmlstarlet esc "$DB_JDBC_URL")"
  SCHEMA=''
  if [ "$DB_TYPE" != "mysql" ]; then
    SCHEMA='<schema-name>public</schema-name>'
  fi
  if [ -n "$JNDI_DATASOURCE" ]; then
    configureContainerDS
  fi
fi
if [ -n "$USE_SSL_PROXY" ]; then
  echo "Use SSL Proxy"
  cp ${BAMBOO_INST}/conf/server.xml ${BAMBOO_INST}/conf/server-backup.xml
  xmlstarlet ed --insert "/Server/Service/Connector" --type attr -n scheme -v "https" ${BAMBOO_INST}/conf/server-backup.xml |
    xmlstarlet ed --insert "/Server/Service/Connector" --type attr -n proxyName -v "$USE_SSL_PROXY" |
    xmlstarlet ed --insert "/Server/Service/Connector" --type attr -n proxyPort -v "443" > ${BAMBOO_INST}/conf/server.xml
fi
#xmlstarlet ed --insert "/Server/Service/Connector" --type attr -n secure -v "true"