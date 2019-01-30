#!/usr/bin/env python

import jmespath
import argparse
import csv
import sys
from terminaltables import SingleTable
from aws_queries import query, AVAILABILITYZONE


def availability_zones(environment,table_flag=False):
 
  field_names = ['Environment','Name']
  availability_zone_json = query('describe-availability-zones',environment)
  availability_zone_data = jmespath.search(AVAILABILITYZONE, availability_zone_json)
  
  csv_data = [
    [environment,availability_zone['name']]
    for availability_zone in availability_zone_data
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
  availability_zones(ENVIRONMENT,table_flag=True)

 
