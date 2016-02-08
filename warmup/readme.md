# Compiling and running java files

Compile the java files with

`javac searchclient/*.java`

and run the level with

`java -jar server.jar -l "levels/SAD2.lvl" -c "java searchclient.SearchClient"`

where you choose the appropriate level.
Add the `-g 60` flag to get a graphical solution, otherwise the solution is printed to the terminal.
