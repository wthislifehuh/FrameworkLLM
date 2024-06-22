class Optimizer:
    # Initialize the Optimizer with a Sieve object
    def __init__(self, sieve):
        self.sieve = sieve

    # Analyze a batch of sentences using the Sieve's LLM analysis
    def analyze_batch(self, sentences):
        return self.sieve.analyse_sentences(sentences)

    # Check the results of the batch analysis
    def check_batch_results(self, results, sentences):
        return self.sieve.check_results([results], len(sentences), sentences)

    # Use binary search to find the optimal number of inputs in a single prompt
    def binary_optimization(self, sentences):
        low, high = 1, len(sentences)
        optimal_batch_size = low

        while low <= high:
            mid = (low + high) // 2
            print(f"Trying batch size: {mid}")

            # Create a batch of sentences with the current batch size
            batch_sentences = dict(list(sentences.items())[:mid])
            results = self.analyze_batch(batch_sentences)

            if self.check_batch_results(results, batch_sentences):
                optimal_batch_size = mid
                low = mid + 1  # Try a larger batch size
            else:
                high = mid - 1  # Try a smaller batch size

        return optimal_batch_size

    # Optimize the number of inputs in a single prompt for the given sentences.
    def optimize(self, sentences):
        if self.sieve.is_valid:
            print(f"Trying batch size: {len(sentences)}")
            return len(sentences)
        else:
            return self.binary_optimization(sentences)