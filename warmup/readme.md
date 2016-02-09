# Compiling and running java files

Compile the java files with

`javac searchclient/*.java`

and run the level with

`java -jar server.jar -l "levels/SAD2.lvl" -c "java searchclient.SearchClient --strategy=STRATEGY"`

where you choose the appropriate level, and `STRATEGY` can be either `BFS, DFS, A*, WA*, Greedy`. Default is `BFS`.
Add the `-g 40` flag to get a graphical solution, otherwise the solution is printed to the terminal. This gives GUI with 40 frames per second.

# Benchmarking
[Overleaf document with our benchmarks](https://www.overleaf.com/read/svkqsbrmwyjw)
