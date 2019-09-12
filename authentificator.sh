#!/bin/bash

python ./main.py $CERTBOT_DOMAIN $CERTBOT_VALIDATION
echo 'DNS updating success! Wait for applying...'
sleep 10
echo 'Success!'