#!/bin/bash

cd /home/django/LBS

# Enable export of KEY=VALUE variables to environment
set -o allexport
# Read env variables from file created in entrypoint.sh on startup,
# escaping punctuation which has meaning in bash.
# Via https://stackoverflow.com/questions/19331497
source <(cat /home/django/full_env_for_cron.env | \
    sed -e '/^#/d;/^\s*$/d' -e "s/'/'\\\''/g" -e "s/=\(.*\)/='\1'/g")
# Turn off export beyond here, though probably doesn't matter in this case.
set +o allexport

# Set variables needed to run the Django management command for the 
# previous month, for all units, sending email.

YEAR=`date -d 'last month' "+%Y"`  # 4-digit year
MONTH=`date -d 'last month' "+%m"` # 2-digit month, 01-12

echo "Running reports for ${YEAR}-${MONTH} via $0"

# TESTING: 21 | DIIT Software Development
/usr/local/bin/python /home/django/LBS/manage.py run_qdb_reporter \
--year ${YEAR} \
--month ${MONTH} \
--unit 21 \
--email \
--o akohler@library.ucla.edu
