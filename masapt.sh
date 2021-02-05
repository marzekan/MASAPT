#!/bin/bash


# Function that runs on Keyboard Interrupt event (Ctrl + C)
control_c() {
  # Kill all MASAPT proccesses that are already running.
  for pid in $(ps -ef | grep -E 'Explorer|Coordinator|SQLinjector|Reporter' | awk '{print $2}'); do kill -9 $pid; done
  exit
}
# Call interrupt event function
trap control_c SIGINT

# --------------- Run agents --------------------

printf "Starting MASAPT...\n"
printf "You can kill the program by hitting Crtl + C\n\n"

python Explorer/explorer.py -t localhost/sqlilabs/Less-1 &

sleep 3

python Coordinator/coordinator.py &

sleep 3

python SQLinjector/sqlinjector.py &

sleep 3

python Reporter/reporter.py &

wait






# broj ejabber procesa, == 2 ako ejabberdctl nije upaljen, == 4 ako je upaljen.
ejabber_proc_num=$(ps aux | grep ejabberd -c)

# if broj ejabber procesa nije veci od 2 pnda pali ejabberdctl start
