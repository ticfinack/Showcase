import dns.resolver
from scapy.all import *
import logging
import sys
import getopt

# specify logging file
logging.basicConfig(format='%(levelname)s:%(asctime)s:%(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='Recon.log', encoding='utf-8', level=logging.DEBUG)

# create function to get command line arguments for domain, subdomain file, and delimiter
def getArgs(argv):
    global domain
    global file
    global delimiter
    opts, args = getopt.getopt(argv,"ht:f:d:",["domain=","file=","delimiter="])
    for opt, arg in opts:
        if opt == '-h':
            print('ReconAutomation.exe -t <target domain> -f <file> -d <delimiter>')
            sys.exit()
        elif opt in ("-t", "--domain"):
            domain = arg
        elif opt in ("-f", "--file"):
            file = arg
        elif opt in ("-d", "--delimiter"):
            delimiter = arg

# call getArgs function
getArgs(sys.argv[1:])

# catch exception if no command line arguments are passed
try:
    domain
except NameError:
    print('ReconAutomation.exe -t <target domain> -f <file> -d <delimiter>')
    sys.exit()

# catch exception if no delimiter is passed
try:
    delimiter
except NameError:
    delimiter = None
    
# catch exception if no file is passed
try:
    file
except NameError:
    file = ["ns","app","gw","vps","www","ww","mail","email","mx","smtp","portal","owa","exchange","vpn","admin","test","dev","intranet","gateway","secure","admin","help","support","webmail","autodiscover","sharepoint","ftp","sip","lyncdiscover","lyncdiscoverinternal","meet","dialin","meet","sipexternal","sipinternal","sipfed","sipfedext","meet","dialin","lync"]

logging.info("Target Domain: '%s'" % domain)
logging.info("Target Subdomains File: '%s'" % file)
logging.info("Delimiter: '%s'" % delimiter)

# declare variables
targetIPs = []

# create a function for looking up the PTR record of an IP address
def ReverseDNS(ip):
    try:
        answer = dns.resolver.resolve_address(ip, 'PTR')
        for rdata in answer:
            logging.info("IP: %s resolves to Domain: %s" % (ip, rdata.target))
            return "%s" % rdata.target
    except:
        pass

# create a function for looking up the dns record of a domain name
def DNSRequest(domain, type):
    try:
        print("Checking: %s.........................." % domain, end='\r')
        answer = dns.resolver.resolve(domain, type)
        for rdata in answer:
            if type != 'A':
                logging.info("Domain: %s is handled by NS: %s" % (domain, rdata.target))
                nsaddr = DNSRequest(rdata.target, 'A')
                if nsaddr is not None:
                    logging.info("NS: %s resolves to IP: %s" % (rdata.target, nsaddr))
                    return "%s" % nsaddr
            else:
                logging.info("Domain: %s resolves to IP: %s" % (domain, rdata.address))
                return "%s" % rdata.address
    except:
        pass

# create a function for iterating through subdomains of the target parent domain
def SubdomainSearch(domain, dictionary, nums):
    global targetIPs
    targetIPs.append(DNSRequest(domain, 'NS'))
    for word in dictionary:
        subdomain = word+"."+domain
        targetIPs.append(DNSRequest(subdomain, 'A'))
        if nums:
            for i in range(0,10):
                s = word+str(i)+"."+domain
                targetIPs.append(DNSRequest(s, 'A'))

# specify ports to scan on discovered hosts
ports = [20,21,22,25,80,53,110,143,443,445,465,587,993,1433,3389,8080,8443,5060,5061,5080,5081]

# create a function for syn scan
def SynScan(host):
    print("Checking for listening ports at %s.........................." % host, end='\r')
    ans,unans = sr(IP(dst=host)/TCP(dport=ports,flags="S"),inter=0.5,timeout=10,verbose=1)
    logging.info("Open TCP ports at %s:" % host)
    for (s,r,) in ans:
        if s.haslayer(TCP) and r.haslayer(TCP):
            if s[TCP].dport == r[TCP].sport:
                logging.info(s[TCP].dport)
    print("\n")

# create a function for dns scan
def DNSScan(host, domain):
    print("Checking for existence of DNS server at %s.........................." % host, end='\r')
    ans,unans = sr(IP(dst=host)/TCP(dport=53)/DNS(rd=1,qd=DNSQR(qname=domain)),retry=2,timeout=4,verbose=0)
    if ans:
        logging.info("DNS Server at %s"%host)
    if unans:
        ans,unans = sr(IP(dst=host)/UDP(dport=53)/DNS(rd=1,qd=DNSQR(qname=domain)),retry=2,timeout=4,verbose=0)

# check if file variable is a string or list
if isinstance(file, list):
    dictionary = file
elif isinstance(file, str):
    # create list of target subdomains to bruteforce from txt file
    dictionary = []
    with open(file,"r") as f:
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
logging.info("Target IPs: "+str(targetIPs))
logging.info("Target Ports: "+str(ports))

# execute syn and dns scan functions for each IP discovered from dns recon
for ip in targetIPs:
    SynScan(ip)
    DNSScan(ip, domain)