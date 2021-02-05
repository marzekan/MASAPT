#!/bin/bash

# broj ejabber procesa, == 2 ako ejabberdctl nije upaljen, == 4 ako je upaljen.
ejabber_proc_num=$(ps aux | grep ejabberd -c)

# if broj ejabber procesa nije veci od 2 pnda pali ejabberdctl start

#pokreni python fajlove

python Reporter/reporter.py &

python Explorer/explorer.py &

wait
