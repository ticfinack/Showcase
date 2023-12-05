# Python Examples

The file above named "automateRecon.py" asks for a target domain and subdomain bruteforce list. It resolves and stores all IP addresses from the subdomain bruteforce list and concatenates a range(1,10) to make sure it queries ns1 or dns3 subdomains as well. The list of IP addresses is then iterated to check for a list of open ports using a SYN scan from the scapy library. I have removed the part that attempts default passwords on ssh/telnet services, I do not want to distribute tools to script kiddies. 

The file above named "Algorithm for file updates in Python.pdf" was created during the lab exercises of the Google Cybersecurity certification. It demonstrates knowledge and use of basic Python methods for accessing/writing files and iterating/manipulating lists. This basic skill is applicable to any script/application that automates cybersecurity tasks.

The file above named "BuildExe.py" creates an executable of the automateRecon.py file.

The file above named "ReconAutomation.exe" is the executable version of the automateRecon.py file.