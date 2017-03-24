#!/bin/sh

# 第一引数でディレクトリパスを指定
DIRPATH="./my_train_data/JPEGImages/*"

for FILE in $DIRPATH
do
  echo "./VOCdevkit/"$FILE >> my_train.txt
done
