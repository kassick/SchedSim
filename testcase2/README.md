# Test-case 1

Two sets of procs:
1. Procs 0 to 3 are i/o bound but have bursts ranging from 9 to 39 (i.e. enough to end in rr-20 and eventually make back to rr-10 when they starve a bit
2. Procs 4 to 6 are very CPU bound, with very minimum I/O. Should end up in FIFO and wait everyone else block
3. Procs 7 to 9 are cpu bound with bursts from 5 to 19 (i.e. they will never fall to rr-20)
