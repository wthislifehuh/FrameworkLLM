from sieve import Sieve

class CircuitBreaker:
    # Initialize the CircuitBreaker with a failure threshold and a dictionary to keep track of failures
    def __init__(self, threshold=1, retries=3):
        self.threshold = threshold
        self.retries = retries
        self.failure_counts = {}

    # Increment the failure count for a given sentence ID
    def increment_failure(self, sentence_id):
        self.failure_counts[sentence_id] = self.failure_counts.get(sentence_id, 0) + 1

    # Check if the failure count for a given sentence ID exceeds the threshold
    def should_break(self, sentence_id):
        return self.failure_counts.get(sentence_id, 0) > self.threshold

    # Process the reanalyzed results in the Sieve object and apply the circuit breaker logic
    def breaker(self, sieve: Sieve, retry_count):
        if retry_count <= self.retries:
            if len(sieve.wrong_sentences) > 0:
                for result in sieve.reanalyzed:
                    for emotion_data in result.get('emotions', []):
                        sentence_id = emotion_data['id']
                        sieve.reanalyzed.remove(emotion_data)
                        if self.should_break(sentence_id):
                            print(f"Breaking circuit for sentence ID: {sentence_id}")
                            sieve.wrong_sentences.remove(sentence_id)
                            continue

                        previous_incorrect = next((item for item in sieve.incorrect_results if item['id'] == sentence_id), None)
                        if previous_incorrect and previous_incorrect == emotion_data:
                            self.increment_failure(sentence_id)
                        else:
                            sieve.correct_results.append(emotion_data)
                            sieve.wrong_sentences.remove(sentence_id)
                return False
            else:
                return True
            
        else:
            return True