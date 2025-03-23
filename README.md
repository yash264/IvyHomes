#  Assignment Ivy Homes
API autocomplete system that extract all possible names.


# Features
1. Build a feature that retries again if API limit hits.
2. Saves the extracted result into names.txt file in sorted order.
3. Made searches on the basis of a-z, aa-zz, 0-9, +=. , etc.
4. Reduces time wastage as sending multiple requests in parrallel using threads.


#  Problem Statement
Given API was undocumented and we have to fetch names as many as possible.

"http://35.200.185.69:8000/v${i}/autocomplete?query=<string>"            where i=1,2,3.
 

#  Challenges 
Initially there were error (429) due to too many requests. Apart from that on applying simple brute force approach in searching takes very long time.


#  Approach 
To optimize the search efficiency we use threads. Threading allows you to execute multiple parts of your program concurrently within a single process, enhancing efficiency and responsiveness, particularly for I/O-bound tasks.


# Installation & SetUp
Install Python

Clone this repository

pip install requests

python appV${i}.py        where i=1,2,3.


#  Result
For V1 - 
Total names collected: 6720.
Total API requests made: 676


For V2 -
Total names collected: 7177.
Total API requests made: 1296


For V3 -
Total names collected: 7308.
Total API requests made: 1600
