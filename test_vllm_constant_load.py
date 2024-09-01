import requests
import concurrent.futures
import time
import random
import logging
import statistics
from openai import OpenAI

# Set up logging
logging.basicConfig(
    filename='api_errors.log',
    filemode='a',  # Append mode
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.ERROR
)

# Console logging
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(console_handler)

# List of different payloads for the API request
payloads = [
    "tell me about U.S. history",
    "explain quantum mechanics",
    "how does a neural network work?",
    "what are the benefits of renewable energy?",
    "describe the Great Wall of China",
    "who is Albert Einstein?",
    "what is the capital of France?",
    "summarize the plot of Moby Dick",
    "how to bake a chocolate cake?",
    "explain the theory of relativity"
]

# Initialize the OpenAI Client with your RunPod API Key and Endpoint URL
client = OpenAI(
    api_key="9NSK8DSVTMQSIO9KRFE826A2ZMXCRF2HLMM0M4QJ",
    base_url="https://api.runpod.ai/v2/xwxenoulxhwbxi/openai/v1",
)

response_times = []  # List to store the response times to the first chunk
chunk_intervals = []  # List to store the time intervals between chunks

def send_request():
    """Function to send a single request to the API and measure response time."""
    try:
        # Randomly pick one payload from the list
        prompt = random.choice(payloads)

        start_time = time.time()  # Record the start time of the request

        # Create a chat completion stream
        response_stream = client.chat.completions.create(
            model="NinjaLLM",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=100,
            stream=True,
        )

        # Measure the time taken to receive the first chunk of data
        first_chunk_time = time.time() - start_time
        response_times.append(first_chunk_time)  # Record the time taken to the first chunk

        # Stream the response and measure the time between chunks
        previous_chunk_time = time.time()  # Initialize previous chunk time
        for response in response_stream:
            current_chunk_time = time.time()
            print(response.choices[0].delta.content or "", end="", flush=True)
            
            # Calculate the interval between this chunk and the previous one
            chunk_interval = current_chunk_time - previous_chunk_time
            chunk_intervals.append(chunk_interval)  # Store the interval
            previous_chunk_time = current_chunk_time  # Update previous chunk time

    except Exception as e:
        error_message = f"Request failed: {e}"
        logging.error(error_message)  # Log error to file and console
        print(error_message)

def calculate_summary_statistics(times, description, output_file):
    """Function to calculate and print summary statistics."""
    if times:
        min_time = min(times)
        max_time = max(times)
        avg_time = statistics.mean(times)
        p70 = statistics.quantiles(times, n=100)[69]
        p80 = statistics.quantiles(times, n=100)[79]
        p90 = statistics.quantiles(times, n=100)[89]

        print(f"\nSummary of {description}:")
        print(f"Min Time: {min_time:.4f} seconds")
        print(f"Max Time: {max_time:.4f} seconds")
        print(f"Average Time: {avg_time:.4f} seconds")
        print(f"P70: {p70:.4f} seconds")
        print(f"P80: {p80:.4f} seconds")
        print(f"P90: {p90:.4f} seconds")

        # Save the summary statistics to a file
        with open(output_file, 'a') as f:
            f.write(f"\nSummary of {description}:\n")
            f.write(f"Min Time: {min_time:.4f} seconds\n")
            f.write(f"Max Time: {max_time:.4f} seconds\n")
            f.write(f"Average Time: {avg_time:.4f} seconds\n")
            f.write(f"P70: {p70:.4f} seconds\n")
            f.write(f"P80: {p80:.4f} seconds\n")
            f.write(f"P90: {p90:.4f} seconds\n")
    else:
        print(f"\nNo data to display for {description}.")

def save_time_data(times, file_name):
    """Function to save time data to a file."""
    with open(file_name, 'w') as f:
        for time_value in times:
            f.write(f"{time_value:.4f}\n")

def constant_load_test(duration=15, max_workers=10):
    """Function to send a constant number of requests in parallel."""
    start_time = time.time()
    
    while (time.time() - start_time) < duration * 60:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(send_request) for _ in range(max_workers)]
            concurrent.futures.wait(futures)
        
        print(f"Completed batch with {max_workers} workers.")
        time.sleep(2)  # Wait before starting the next batch

    # Calculate and print summary statistics for both metrics
    calculate_summary_statistics(response_times, "Response Times to First Chunk", 'response_times_summary.txt')
    calculate_summary_statistics(chunk_intervals, "Time Intervals Between Chunks", 'chunk_intervals_summary.txt')

    # Save raw data to files
    save_time_data(response_times, 'response_times.txt')
    save_time_data(chunk_intervals, 'chunk_intervals.txt')

if __name__ == "__main__":
    # Adjust the max_workers parameter to set the desired load
    constant_load_test(duration=2, max_workers=1)  # Run the test for 2 minutes with 10 parallel requests
