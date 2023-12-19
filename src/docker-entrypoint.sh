#!/bin/sh
. venv/bin/activate
if [ "$1" = "sh" ]; then
	shift
	exec sh "$@"
fi
python "$@"
