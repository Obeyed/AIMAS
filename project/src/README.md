# Running the client
The client is run with `python3 client.py`.
A version of the Python programming language version 3 is required.
The client was tested with python version 3.4.3.

## Run with Java server
The client can be run from the parent folder of `src/` (`project/`) with
```
java -Dsun.java2d.opengl=true -jar resources/environment/server.jar -c "python3 src/client.py" -g 29 -l competition_levels/MAteamhal.lvl
```
If you do not need to manually enable hardware acceleration, then omit the `-Dsun.java2d.opengl=true` flag.
