It works very simply. You only need to download the code, set up the requirements, and transfer the .db file to the script directory. After this, simply start build_graph.py and wait for a bit. After about 30 seconds, the plot will open.

I decided to split the filtered data into chunks of 100k dots. This is done to ensure that the plot remains interactive, as having too many objects can cause lag. You can switch between chunks by pressing the buttons ![image](https://github.com/travis-joe/sybil-hunt-tool/assets/166750254/6d0b78f8-dd3c-43ee-9e7d-960180dc16b2).

By pressing this button ![image](https://github.com/travis-joe/sybil-hunt-tool/assets/166750254/9308fa3b-fca4-4058-a226-36c74bb69c64), you can enter interactive plot mode and manipulate its size. By unpressing it, you will return to normal mode, in which you will be able to select dots ![image](https://github.com/travis-joe/sybil-hunt-tool/assets/166750254/92857942-5854-460f-9964-617fed4b194e)
 and display their data in the terminal. ![image](https://github.com/travis-joe/sybil-hunt-tool/assets/166750254/d968ff54-c316-4f5e-90ad-5cd32181a85d).

The second script, called stats.py, allows you to get stats of the wallets listed in the report.md file. Simply copy the data from the terminal and dump it into report.md. It will work, and the results will be printed to the terminal as well as uploaded to output.py.
