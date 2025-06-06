import requests
import json
from secretkeys import API_KEY
# Your input data
input_data = {
    "automata": 1,
    # "operating System": 1,
    # "AI": 1
}

# DeepSeek API configuration
# API_URL = "https://api.deepseek.com/v1/chat/completions"  # Check the actual API endpoint
API_URL='https://openrouter.ai/api/v1/chat/completions'


headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def generate_questions_for_topic(topic, count):
    questions = []

    for _ in range(count):
        # Construct a prompt specific to the topic
        prompt = f"""
        Generate a multiple choice question about {topic} with 4 options (A, B, C, D) and indicate the correct answer.
        Return the response in JSON format with these keys be case sensitive with the key:
        - 'topic' (capitalize the first letter)
        - 'question'
        - 'optiona'
        - 'optionb'
        - 'optionc'
        - 'optiond'
        - 'correctoption' (just the letter, e.g., 'A', 'B', etc.)
        """

        data = {
            "model": "deepseek/deepseek-chat-v3-0324:free",  # or whatever model you're using
            "messages": [{"role": "user", "content": prompt}],
            # "temperature": 0.7
        }

        response = requests.post(API_URL, headers=headers, json=data)

        if response.status_code == 200:
            try:
                # Extract the content from the response
                content = response.json()['choices'][0]['message']['content']

                # Sometimes the API might return markdown or other formatting, so we need to extract JSON
                if '```json' in content:
                    content = content.split('```json')[1].split('```')[0]

                question_data = json.loads(content)
                questions.append(question_data)
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error processing response for {topic}: {e}")
                # print(f"Response content: {content}")
        else:
            print(f"API request failed for {topic}: {response.status_code}")
            print(response.text)

    return questions

def generate_all_questions(input_data):
    all_questions = []

    for topic, count in input_data.items():
        print(f"Generating {count} questions for {topic}...")
        questions = generate_questions_for_topic(topic, count)
        all_questions.extend(questions)

    return all_questions

# # Generate all questions
# output_data = generate_all_questions(input_data)
# print(output_data)
# # Save to a file or use as needed
# with open('generated_questions.json', 'w') as f:
#     json.dump(output_data, f, indent=2)

# print(f"Generated {len(output_data)} questions in total.")
