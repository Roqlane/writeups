# Trapped in Plain Sight

The goal was to escalate privilege from a simple user. I looked for suids with the command `find / -perm 4000 2>/dev/user` and `xxd` came out. Looking at https://gtfobins.github.io/gtfobins/xxd/, it was really easy to read the flag `xxd flag.txt | xxd -r`
