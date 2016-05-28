#EXPANDING

This file will explain how to easily add new functionality to `RSPET_server.py`

## Steps:
* Add your function to the function block (top of the program) following the specifications stated below
* Add a new entry to `conn_command_func_dict` dictionary and/or `conn_mul_command_func_dict` 
* Add a new entry to `list_connected_commands` and/or `list_connected_mult_commands` (optional)
* Add a new entry to `commands` in `tab.py` in order to enable autocomplete for the new function (optional)
* That's it! Ready to fire it up! Really no need to add any calls in the main body.
* Just type your function's name as a command while using `RSPET_server.py`

## Function specifications:
* Function's arguments must follow the form of `(arrayOfUserProvidedInput, cur_host_con, cur_host_id, handler)`
* Try-Except anything able to throw an exception under normal opperation (maybe log it to a file)
* In order to send data to a host use `send_comm` passing (yourMsg, cur_host_con)
* If `send_comm` returns 1 remote host has closed the connection. 
* Check against the above case and do `handler.remove_host(cur_host_id)` followed by `return 1`
* In order to recieve data from a host use `recv_comm` passing (expectedSize, cur_host_con)
* DO NOT CALL an infinitely recurring function since it will dead-lock the server interface

Did I miss something? Have a question or a request? Feel free to contact me.
