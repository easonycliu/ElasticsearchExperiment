#!/bin/bash

set -m
client_num=5
exp_duration=30

for i in $(seq 1 1 $client_num); do
    python microbenchmark/test_multiclient_request_cache.py true request_cache_evict /dev/null /dev/null &
    sleep 0.1
done

sleep 10

for j in $(seq 1 1 $exp_duration); do
    kill -10 $(ps | grep python | awk '{print $1}')
    sleep 1
done

kill -2 $(ps | grep python | awk '{print $1}')
