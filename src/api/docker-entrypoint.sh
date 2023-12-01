#!/bin/sh
if [ "$1" = "sh" ]; then
	shift
	exec sh "$@"
fi
exec uvicorn api:app "$@"
