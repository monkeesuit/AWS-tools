#!/usr/bin/env python

import jmespath
import argparse
import csv
import sys
from terminaltables import SingleTable
from aws_queries import query, IMAGE


def images(environment,table_flag=False):
 
  field_names = ['Environment','Name','ID','Virtualization Type','Root Type','Owner ID','Create Date']
  image_json = query('describe-images',environment)
  image_data = jmespath.search(IMAGE, image_json)
  
  csv_data = [
    [environment,
     image['name'],
     image['id'],
     image['virtType'],
     image['rootType'],
     image['ownerId'],
     image['createDate']]
    for image in image_data
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
  images(ENVIRONMENT,table_flag=True)

 
