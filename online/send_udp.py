#!/usr/bin/env python

import socket
import struct

def main():
  MCAST_GRP = '234.0.0.1'
  MCAST_PORT = 9999
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
  sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
  with open('sample_question.txt') as f:
	  sock.sendto(f.read().encode('utf-8'), (MCAST_GRP, MCAST_PORT))
if __name__ == '__main__':
  main()
