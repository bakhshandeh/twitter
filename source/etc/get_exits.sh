echo -e "authenticate \"\"\ngetinfo circuit-status\nquit" | nc 127.0.0.1 9051 | grep PURPOSE | cut -d ' ' -f 3 | xargs | sed -e "s/ /,/g"
