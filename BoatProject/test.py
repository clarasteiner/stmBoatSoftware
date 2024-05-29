from subprocess import *

with Popen(['ssh', '-T', 'pi@10.3.6.86'],
           stdin=PIPE, stdout=PIPE, stderr=PIPE,
           universal_newlines=True) as p:
    output, error = p.communicate("""            
        cd /home/pi/Desktop
        ls -l
        """)
    print(1, output)
    print(2, error)
    print(3, p.returncode)

