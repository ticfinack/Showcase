#import socket
import dns.resolver
#import dns.ipv4
from scapy.all import *

# declare variables
targetIPs = []

# create a function for looking up the PTR record of an IP address
def ReverseDNS(ip):
    try:
        answer = dns.resolver.resolve_address(ip, 'PTR')
        for rdata in answer:
            print("IP: %s resolves to Domain: %s" % (ip, rdata.target))
            return "%s" % rdata.target
    except:
        pass

# create a function for looking up the dns record of a domain name
def DNSRequest(domain, type):
    try:
        answer = dns.resolver.resolve(domain, type)
        for rdata in answer:
            if type != 'A':
                print("Domain: %s is handled by NS: %s" % (domain, rdata.target))
                nsaddr = DNSRequest(rdata.target, 'A')
                if nsaddr is not None:
                    print("NS: %s resolves to IP: %s" % (rdata.target, nsaddr))
                    return "%s" % nsaddr
            else:
                print("Domain: %s resolves to IP: %s" % (domain, rdata.address))
                return "%s" % rdata.address
    except:
        pass

# create a function for iterating through subdomains of the target parent domain
def SubdomainSearch(domain, dictionary, nums):
    global targetIPs
    targetIPs.append(DNSRequest(domain, 'NS'))
    for word in dictionary:
        subdomain = word+"."+domain
        print("Checking: %s.........................." % subdomain, end='\r')
        targetIPs.append(DNSRequest(subdomain, 'A'))
        if nums:
            for i in range(0,10):
                s = word+str(i)+"."+domain
                targetIPs.append(DNSRequest(s, 'A'))

# specify ports to scan on discovered hosts
ports = [20,21,22,25,80,53,110,143,443,445,465,587,993,1433,3389,8080,8443,51000,range(52201,52210),5060,5061,5080,5081]
#ports = [range(1,65535)]

# create a function for syn scan
def SynScan(host):
    ans,unans = sr(IP(dst=host)/TCP(dport=ports,flags="S"),inter=0.5,timeout=10,verbose=1)
    print("Open ports at %s:\n" % host)
    for (s,r,) in ans:
        if s.haslayer(TCP) and r.haslayer(TCP):
            if s[TCP].dport == r[TCP].sport:
                print(s[TCP].dport)
    print("\n")

# create a function for dns scan
def DNSScan(host, domain):
    ans,unans = sr(IP(dst=host)/UDP(dport=53)/DNS(rd=1,qd=DNSQR(qname=domain)),retry=4,timeout=10,verbose=0)
    if ans:
        print("DNS Server at %s\n"%host)

# specify target parent domain name
print("\nSpecify the target domain name: ")
domain = input()

# specify the file of target subdomains to bruteforce
print("\nSpecify the file that contains the target subdomains to bruteforce: ")
d = input()

# ask for a file delimiter
print("\nIf the entries in the file are separated by a character, specify the delimiter here, if not, leave blank: ")
delimiter = input()
print("\n")

# create list of target subdomains to bruteforce from txt file
dictionary = []
with open(d,"r") as f:
    if delimiter:
        dictionary = f.read().split(delimiter)
    else:
        dictionary = f.read().split()
SubdomainSearch(domain,dictionary,True)

# remove duplicates from targetIPs list
targetIPs = list(dict.fromkeys(targetIPs))

# remove None from targetIPs list
targetIPs = [x for x in targetIPs if x is not None]

# print targetIPs and ports lists
print("\nTarget IPs: "+str(targetIPs))
print("Target Ports: "+str(ports)+"\n")

# execute syn and dns scan functions for each IP discovered from dns recon
for ip in targetIPs:
    SynScan(ip)
    DNSScan(ip, domain)