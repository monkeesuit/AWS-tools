#!/usr/bin/env python

import jmespath
from aws_queries import query, SECURITYGROUP


def vpc_info(environment):

  vpc_json = query('describe-vpcs',environment)
  vpc_data = jmespath.search(
    "Vpcs[].{id:VpcId, tag:Tags[?Key==`Name`].Value | [0]}",
    vpc_json
  )
  vpc_dict = {
    entry['id']:entry['tag']
    for entry in vpc_data
  }
  return vpc_dict


def subnet_info(environment):

  subnet_json = query('describe-subnets',environment)
  subnet_data = jmespath.search(
    "Subnets[].{id:SubnetId, tag:Tags[?Key==`Name`].Value | [0]}",
    subnet_json
  )
  subnet_dict = {
    entry['id']:entry['tag']
    for entry in subnet_data
  }
  return subnet_dict


def instance_info(environment):

  instance_json = query('describe-instances',environment)
  instance_data = jmespath.search(
    "Reservations[].{id:Instances[].InstanceId | [0], tag:Instances[].Tags[?Key==`Name`].Value | [0] | [0]}",
    instance_json
  )
  instance_dict = {
    entry['id']:entry['tag']
    for entry in instance_data
  }
  return instance_dict


def security_group_info(environment):

  security_group_json = query('describe-security-groups',environment)
  security_group_data = jmespath.search(SECURITYGROUP,security_group_json)

  security_group_dict = {}
  for security_group in security_group_data:

    security_group_dict[security_group['id']] = {
      'name': security_group['name'],
      'members': {}
    }

    for security_group_permission in security_group['ingressPermission']:

      security_group_permission_port_protocol = (
        security_group_permission['portStart'],
        security_group_permission['portEnd'],
        security_group_permission['protocol']
      )
      security_group_permission_ip_addresses = [
        security_group_permission_ip['address']
        for security_group_permission_ip in security_group_permission['ip']
      ]
      security_group_permission_nested_security_group = security_group_permission['sg']
      security_group_permission_members = security_group_permission_ip_addresses + security_group_permission_nested_security_group
      
      security_group_dict[security_group['id']]['members'][security_group_permission_port_protocol] = security_group_permission_members

  return security_group_dict
