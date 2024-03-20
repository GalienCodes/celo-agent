rm -r celo-swapper
find . -empty -type d -delete  # remove empty directories to avoid wrong hashes
autonomy packages lock
autonomy fetch --local --agent celo/celo-swapper && cd celo-swapper

cp $PWD/../ethereum_private_key.txt .
autonomy add-key ethereum ethereum_private_key.txt
autonomy issue-certificates
aea -s run