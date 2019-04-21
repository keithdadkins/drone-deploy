#!/usr/bin/env bash
set -e
if [ "$1" == "aws" ]; then
    shift
    exec aws "$@"
fi
exec "$@"
