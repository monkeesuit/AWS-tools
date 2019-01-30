#!/usr/bin/env python

import jmespath
import argparse
import csv
import sys
from terminaltables import SingleTable
from aws_queries import query, KEYPAIR


def key_pairs(environment,table_flag=False):
 
  field_names = ['Environment','Name']
  key_pair_json = query('describe-key-pairs',environment)
  key_pair_data = jmespath.search(KEYPAIR, key_pair_json)
  
  csv_data = [
    [environment,key_pair['name']]
    for key_pair in key_pair_data
  ]
  csv_data.insert(0,field_names)

  if table_flag==False:
    csv_writer = csv.writer(sys.stdout)
    for line in csv_data:
      csv_writer.writerow(line)
  else:
    table = SingleTable(csv_data)
    table.inner_row_border = True
    print table.table

###############################################################################

if __name__=="__main__":

  parser = argparse.ArgumentParser()
  parser.add_argument('environment',nargs=1)
  args = parser.parse_args()

  ENVIRONMENT=args.environment[0]
  key_pairs(ENVIRONMENT,table_flag=True)

 
