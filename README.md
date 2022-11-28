# knowledge-extractor
is a Python based extractor and can be used to parse various benchmark results, i.e. IOR, HACCIO, IO500 (IOR and MDTEST) and Darshan logs via PyDarshan and map them onto our database schema respectively persist them. 
In addition, systems statistics (such as processor cores, processor architecture, operating system, processor frequency, cache, memory sizes) and user-level file system information for BeeGFS (such as Entry type, EntryID, Metadata node, Stripe pattern) can be extracted and mapped to appropriate database schemas.
The extractor also contains useful methods for creating and deleting database tables.

For automatic execution, the extractor can be defined as an additional executable in JUBE configuration file or batch script and executed sequentially after the actual application or benchmark.
