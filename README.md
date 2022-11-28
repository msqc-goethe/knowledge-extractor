# knowledge-extractor
is a Python based extractor and can be used to parse various benchmark results, i.e. IOR, HACCIO, IO500 (IOR and MDTEST) and Darshan logs via PyDarshan and map them onto our database schema respectively persist them. 
In addition, systems statistics (such as processor cores, processor architecture, operating system, processor frequency, cache, memory sizes) and user-level file system information for BeeGFS (such as Entry type, EntryID, Metadata node, Stripe pattern) can be extracted and mapped to appropriate database schemas.
The extractor also contains useful methods for creating and deleting database tables.

For automatic execution, the extractor can be defined as an additional executable in the JUBE configuration file or batch script and executed sequentially after the actual application or benchmark.

```
<jube>
  <benchmark name="ior" outpath="./bench_run">
    <parameterset name="ior_parameter">
      <parameter name="nodes"  separator=";">16;32;64;128;256;512</parameter>
      <parameter name="blockSize" separator=";">4m;8m;16m</parameter>
      <parameter name="iteration" separator=";">5</parameter>
      <parameter name="transferSize" separator=";">2m</parameter>
      <parameter name="segmentCount"  type="int">5</parameter>
      <parametername="outputPath">/scratch/fuchs/agdino/test/ior_out/16_512</parameter>
    </parameterset>
    <!-- Operation -->
    <step name="pre"> … </step>
    <step name="execute">
      <!-- use existing parameterset -->
      <use>ior_parameter</use>
       <!-- shell command -->
      <do>LD_PRELOAD=/pathToDarshan/lib/libdarshan.so mpirun -n $nodes ior -a mpiio -b   $blockSize -t $transferSize -s $segmentCount -F -i $iteration -o $outputPath -k</do>
      <do>python3 /pathToExtractor/main.py -darshan_path $outputPath<do>
  </benchmark>
</jube>
```
