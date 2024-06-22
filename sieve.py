import pandas as pd
import random
import string
import json
from openai import OpenAI

class Sieve:
    # Initilization
    def __init__(self, filename):
        self.filename = filename
        self.expected_emotions = {'joy', 'sad', 'surprise', 'angry', 'fear', 'neutral'}
        self._correct_results = []
        self._incorrect_results = []
        self._reanalyzed = []
        self.wrong_sentences = []
        self.result_is_valid = False

    # Property Methods
    @property
    def correct_results(self):
        return self._correct_results

    @correct_results.setter
    def correct_results(self, value):
        self._correct_results = value

    @property
    def incorrect_results(self):
        return self._incorrect_results

    @incorrect_results.setter
    def incorrect_results(self, value):
        self._incorrect_results = value

    @property
    def wrong_sentences(self):
        return self._wrong_sentences

    @wrong_sentences.setter
    def wrong_sentences(self, value):
        self._wrong_sentences = value

    @property
    def reanalyzed(self):
        return self._reanalyzed

    @reanalyzed.setter
    def reanalyzed(self, value):
        self._reanalyzed = value

    @property
    def is_valid(self):
        return self.result_is_valid

    @is_valid.setter
    def is_valid(self, value):
        self.result_is_valid = value

    # ID generation for each sentence
    def generate_random_id(self, prefix_length=2, suffix_length=2, existing_ids=set()):
        while True:
            random_id = ''.join(random.choices(string.ascii_uppercase, k=prefix_length)) + \
                        ''.join(random.choices(string.digits, k=suffix_length))
            if random_id not in existing_ids:
                existing_ids.add(random_id)
                return random_id

    def assign_ids(self, sentences):
        existing_ids = set()
        return {self.generate_random_id(existing_ids=existing_ids): sentence for sentence in sentences}

    # Read the sentences from CSV file
    def read_sentences(self, start_row, num_rows):
        sentences_df = pd.read_csv(self.filename, skiprows=range(1, start_row), nrows=num_rows, encoding="latin1", usecols=['sentences'])
        sentences = sentences_df['sentences'].tolist()
        sentences_with_ids = self.assign_ids(sentences)
        print(f"Sentence: {sentences_with_ids}")
        return sentences_with_ids

    # LLM for Emotion analysis
    def analyse_sentences(self, sentences):
        client = OpenAI(api_key='API_KEY')
        prompt = f"""
        {sentences}
        Analyse the emotions of the sentences (with ID given) above and return a JSON array as the result. The emotions could be expressed in the following: joy, sad, surprise, angry, fear, neutral. Provide emotions confidence score on a scale of 1-100. The JSON must have these fields: id, emotion, emotion_score.
        """
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_format={"type":"json_object"},
            messages=[
                {"role": "system", "content": "You are an expert in text emotion analysis. Provide the data schema in valid JSON with format of: "+json.dumps({'emotions': [{'id': 'AA11', 'emotion': 'sad', 'emotion_score': 85}]} )},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
        )
        try:
            generated_text = completion.choices[0].message.content
            return json.loads(generated_text)
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    # Evaluate the results
    def check_results(self, results, sentence_count, sentences):
        formatted_output = {'emotions': []}
        # Check format and structure of the results
        for result in results:
            if not self.is_valid_json(result):
                self.wrong_sentences.append(sentences)
                self.incorrect_results.append(result)
                print(f"Result in completely different JSON format")
                continue
            
            # Missing/additional results
            emotions = result.get('emotions', [])
            if len(emotions) != sentence_count:
                if len(emotions) > sentence_count:
                    print(f"{len(emotions) - sentence_count} additional results found")
                    correct = [emotion_data for emotion_data in emotions if emotion_data['id'] in sentences]
                    formatted_output['emotions'].extend(correct)
                    self.correct_results = [formatted_output] 
                    incorrect = [emotion_data for emotion_data in emotions if not (emotion_data['id'] in sentences)]
                    self.incorrect_results.extend(incorrect)
                else:
                    print(f"{sentence_count - len(emotions)} missing results")
                    incorrect_sentences = {sentences_data for sentences_data in sentences if sentences_data not in [e['id'] for e in emotions]}
                    self.wrong_sentences.extend(incorrect_sentences)
                continue
            
            # Invalid results (that are not prompted)
            for emotion_data in emotions:
                if emotion_data['emotion'] not in self.expected_emotions:
                    print(f"Invalid emotions found")
                    self.wrong_sentences.append({sentences_data for sentences_data in sentences if sentences_data == emotion_data['id']})
                else:
                    formatted_output['emotions'].append(emotion_data)
                    self.correct_results = [formatted_output]

        if not self.wrong_sentences:
            print("All results are correct. No further analysis needed.")
            self.is_valid = True
            return True
        else:
            print("Incorrect: ", self.wrong_sentences)
            self.is_valid = False
            self.analyze_incorrect_results()
            return False

    # Check structure/format of the results
    def is_valid_json(self, json_obj):
        expected_keys = {'id': str, 'emotion': str, 'emotion_score': int}

        if not isinstance(json_obj, dict):
            print("Invalid JSON structure: Root element is not a dictionary")
            return False

        if 'emotions' not in json_obj or not isinstance(json_obj['emotions'], list):
            print("Invalid JSON structure: 'emotions' key missing or not a list")
            return False

        for item in json_obj['emotions']:
            if not isinstance(item, dict):
                print(f"Invalid JSON structure: Item {item} is not a dictionary")
                return False

            for key, expected_type in expected_keys.items():
                if key not in item:
                    print(f"Invalid JSON structure: Key '{key}' missing in item {item}")
                    return False
                if not isinstance(item[key], expected_type):
                    print(f"Invalid JSON structure: Key '{key}' in item {item} is not of type {expected_type.__name__}")
                    return False
        return True

    # Analyse incorrect result again
    def analyze_incorrect_results(self):
        for sentence in self.wrong_sentences:
            analyzed_result = self.analyse_sentences(sentence)
            self.reanalyzed.append(analyzed_result)

        print("Reanalysis completed. Results stored in reanalyzed.")
        print(self.reanalyzed)
