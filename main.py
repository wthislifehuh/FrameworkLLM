from sieve import Sieve
from circuit_breaker import CircuitBreaker
from optimizer import Optimizer
import time

def run_framework():
    start_time = time.time()

    # Initialization
    sieve = Sieve("sentence.csv")
    circuit_breaker = CircuitBreaker()
    optimizer = Optimizer(sieve)
    start_row, num_rows = 0, 10

    # Read and analyze sentences
    sentences_with_ids = sieve.read_sentences(start_row, num_rows)
    result = sieve.analyse_sentences(sentences_with_ids)

    # Sieve analyses result, goes into loop if there are any errors, 
    # circuit breaker stops analysis for the output that is consistently incorrect for twice (repeated error)
    if sieve.check_results([result], num_rows, sentences_with_ids):
        print(f"Final results: {result}")
    else:
        retry_count = 0
        while True:
            sieve.analyze_incorrect_results()
            if circuit_breaker.breaker(sieve):
                break
            retry_count += 1
        print(f"Final results: {sieve.correct_results}")

    # Optimize the batch size
    optimal_batch_size = optimizer.optimize(sentences_with_ids)
    print(f"Optimal batch size: {optimal_batch_size}")

    # Calculate and print the elapsed time
    elapsed_time = time.time() - start_time
    print("Processing completed")
    print(f"Processing time: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    run_framework()
