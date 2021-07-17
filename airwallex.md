## Instruction

As discussed, the next step in our interview process is for you to complete the Airwallex coding challenge. Please find the instructions for the challenge [here.](https://drive.google.com/file/d/17RNueLW8XD4uhHk3gOevauX_NWDcXdCH/view?usp=sharing)
There is no hard time limit on this but we would love for you to send it back to me by Monday 19th July 9am so make sure you put your best foot forward We’re primarily looking for a correct solution, but we are an engineering company at our core, so give some thought to how your code is structured, levels of abstraction, testing and extensibility for the future.
Please do the assessment in your coding language of choice. We have no preference.

---

## Design Document

> You may assume that for each currency pair, currency conversion rates are streamed at a constant rate of one per second. ie. for two consecutive "CNYAUD" entries in the input file, they will have timestamps that differ by one second

Based on the assumption that new data point for each conversion rates are received every second, the number of data points received per second is
$$
P(n,2)=\frac{n}{(n-2)!}
$$
Where $n$ is the number of currencies that Airwallex supports. 

Since spot rates are asymmetric, I'm using permutation instead of combination.

If $n=100$, then $P(100, 2)=9900$ data points will need to be processed every second.



For each data point, the program needs to

- Calculate the percentage difference between the new spot rate and the last 5-minute moving average.
- Alert (print to console) if the percentage difference is greater than or equal to 10%.
- Update the 5-minute moving average for that particular currency pair.



For each pair of currency, 5-minute moving average is based on $60 \times 5=300$ data points. Some options we have:

1. Use a queue to store the last 300 data points. Every time a new spot rate is received, we dequeue the oldest element and enqueue the latest element. Then we calculate the average by summing the 300 data points and dividing by 300.

2. Let $x_{i,j,t}$ be the moving average of the spot rate from currency $i \rightarrow j$ for the 5-minute interval ending at time $t$, and $r_{i,j,t}$ be the spot rate from currency $i \rightarrow j$ at time $t$. Then,
	$$
	x_{i,j,t} = \frac{(300 \times x_{i,j,t-1}) - r_{i,j,t-300} + r_{i,j,t}}{300}
	$$

If the rate of data stream is fixed at around 1 second per data point, then it can be argued that the time complexity of option 1 is $O(1)$ since the size of the queue will not grow beyond 300. However, that still means for every new data point the program would need to sum up 300 data points and calculate the average. On the other hand, option 2 takes advantage of the previously computed value to derive the updated 5-minute moving average, making it much more efficient than option 1.

Assumption: Since we are dealing with currency exchange, whenever there is a change greater than 10% from the moving average, we want to know about it, and respond to the change as quickly as possible. Therefore, speed is critical.



Due to global interpreter lock, Python may not be the best language of choice for solving this problem.

