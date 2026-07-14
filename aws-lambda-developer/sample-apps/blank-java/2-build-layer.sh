#!/bin/bash
set -eo pipefail

if [ $1 ]
then
  if [ $1 = mvn ]
  then
    mvn prepare-package
  fi
else
  gradle packageLibs
  mv build/distributions/workspace.zip build/blank-java-lib.zip
fi