#!/usr/bin/env python

from subprocess import Popen, PIPE
from collections import namedtuple, OrderedDict
import jmespath
import argparse
import getpass
import pprint
import json
import sys
from aws_queries import SECURITYGROUP, INSTANCE, query


def define_ip_addresses(environment):

  security_group_json = query('describe-security-groups',environment)
  instance_json = query('describe-instances',environment)
  security_group_data = jmespath.search(SECURITYGROUP, security_group_json)
  instance_data = jmespath.search(INSTANCE, instance_json)
  
  ip_entry = namedtuple(
    typename='ipEntry',
    field_names=['address', 'tag', 'security_group_id', 'security_group_name']
  )
  
  security_group_ip_entries = [
    ip_entry(
      address = ip['address'],
      tag = ip['tag'],
      security_group_id = security_group['id'],
      security_group_name = security_group['name']
    )
    for permission in ['ingressPermission','egressPermission']
    for security_group in security_group_data
    for rule in security_group[permission]
    for ip in rule['ip']
  ]
  
  instance_ip_entries = [
    ip_entry(
      address = instance['ip'][ip_type]+"/32",
      tag = instance['tag'],
      security_group_id = "Instance IP",
      security_group_name = "Instance IP"
    )
    for ip_type in ['pub','prv']
    for instance in instance_data
    if instance['ip'][ip_type] != None
  ]
  
  ip_entries = security_group_ip_entries + instance_ip_entries
  
  # ip addresses can appear multiple times and with many tags
  # so we must add all encountered tags and other relevant info for a given ip
  ip_dictionary = {}
  for ip_entry in ip_entries:
    key = ip_entry.address
    value = ip_dictionary.get(key, [])
    value.append(ip_entry)
    ip_dictionary[key] = value

  return ip_dictionary


def name_ips(ip_dictionary):

  ip2name = {
    ip:ip_info.tag
    for ip in ip_dictionary
    for ip_info in ip_dictionary[ip]
    if ip_info.tag != None
  }

  return ip2name


def find_inconsistently_named_ips(environment,ip_dictionary):

  inconsistent_ips = []
  named_ips = name_ips(ip_dictionary)

  for ip in named_ips:
    tags = [ip_info.tag for ip_info in ip_dictionary[ip]]
    if all(x==named_ips[ip] for x in tags): continue
    inconsistent_ips.append(ip_dictionary[ip])

  inconsistent_ips=sorted(inconsistent_ips, key=lambda ip_info:ip_info[0].address)

  for ip in inconsistent_ips:
    for ip_info in ip:
      print ','.join([
        environment,
        str(ip_info.address),
        str(ip_info.tag),
        str(ip_info.security_group_id)
      ])
    print '-' * 80


def find_no_name_ips(environment,ip_dictionary):

  no_tag = []

  for ip in ip_dictionary:
    tags = [ip_info.tag for ip_info in ip_dictionary[ip]]
    if all(x==None for x in tags): no_tag.append(ip_dictionary[ip])

  no_tag=sorted(no_tag, key=lambda no_tag:no_tag[0].address)

  for ip in no_tag:
    print ','.join([environment,ip[0].address])
    for ip_info in ip:
      print "  * {}".format(ip_info.security_group_id)
    print '-' * 80


def find_temp_ips(environment,ip_dictionary):
  # return ips in an environment that have 'temp' in their tag

  temp_ips = []
  for ip in ip_dictionary:
    for ip_entry in ip_dictionary[ip]:
      if ip_entry.tag != None and "temp" in ip_entry.tag:
        temp_ips.append({
          "address":ip_entry.address,
          "tag":ip_entry.tag
        })
        break

  return temp_ips
  #for ip in temp_ips:
  #  print ip["address"]
  #  for entry in ip_dictionary[ip["address"]]:
  #    print entry.security_group_id
  #  print '*'*80
   



###############################################################################

if __name__=="__main__":

  parser = argparse.ArgumentParser()
  parser.add_argument('environment',nargs=1)
  parser.add_argument('report',nargs=1)
  args = parser.parse_args()

  ENVIRONMENT=args.environment[0]
  REPORT=args.report[0]

  if REPORT=="name":
    ip_dictionary = define_ip_addresses(ENVIRONMENT)
    pprint.pprint(name_ips(ip_dictionary))
  elif REPORT=="inconsistent-tags":
    ip_dictionary = define_ip_addresses(ENVIRONMENT)
    find_inconsistently_named_ips(ip_dictionary)
  elif REPORT=="no-tags":
    ip_dictionary = define_ip_addresses(ENVIRONMENT)
    find_no_name_ips(ip_dictionary)
  elif REPORT=="temp-tags":
    ip_dictionary = define_ip_addresses(ENVIRONMENT)
    find_temp_ips(ENVIRONMENT,ip_dictionary)
  else:
    print "USAGE: aws-ip {environment} {report}"
    print "Available Reports: name, inconsistent-tags, no-tags"
    sys.exit(1)
  sys.exit(0)
