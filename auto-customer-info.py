import requests
from requests.auth import HTTPBasicAuth
from openai import OpenAI
import json

# Basic authentication credentials
username = 'hailong.yang@runpod.io/token'
password = ''

# Base URL for Zendesk API
base_url = "https://runpodinc.zendesk.com/api/v2/tickets/{}/comments"

# Initialize the OpenAI Client with your RunPod API Key and Endpoint URL
client = OpenAI(
    api_key="",
)

# Loop through tickets 1 to 7000
for ticket_id in range(6950, 7005):
    # Make a GET request for each ticket's comments
    response = requests.get(base_url.format(ticket_id), auth=HTTPBasicAuth(username, password))
    
    # Check if the request was successful
    if response.status_code == 200:
        comments_data = response.json().get("comments", [])
        
        # Check if there are any comments
        if comments_data:
            # Extract the author_id of the first comment
            initial_author_id = comments_data[0].get("author_id")
            created_at = comments_data[0].get("created_at")
            author_name = comments_data[0].get("via", {}).get("source", {}).get("to", {}).get("name", "Unknown")
            author_email = comments_data[0].get("via", {}).get("source", {}).get("to", {}).get("address", "Unknown")
            combined_content = created_at + ", " + author_name + ", " + author_email + ", "
            
            # Filter comments by the author_id of the first comment
            filtered_comments = [comment for comment in comments_data if comment.get("author_id") == initial_author_id]
            
            # Combine the information of the filtered comments
            for comment in filtered_comments:
                plain_body = comment.get("plain_body")

                # Append each comment's plain body to the combined content
                combined_content += f"""
                Comment: {plain_body}
                """
                
            # Only call OpenAI API if there are valid filtered comments
            if combined_content.strip():
                # Print the combined content before sending (for debugging)
                # print(author_name + author_email + combined_content)

                # Pass the filtered data to OpenAI API
                completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        { 
                            "role": "system", 
                            "content": """You are a helpful assistant. Your task is to extract specific details from customer data. Focus on gathering the following information:
                            - Timestamp (time)
                            - Customer's name
                            - Customer's email
                            - Customer's company (if mentioned)
                            - Customer's company website (if mentioned)
                            - A description of their business and how they use GPUs (if mentioned)
                            - Type of GPU they are looking for (if mentioned)
                            - Quantity of GPUs they need (if mentioned)
                            - Link to their company website (if available)
                            - AI models they are leveraging (if mentioned)
                            - Usage profile: whether their usage is higher during the day or night and in what proportions (if mentioned)

                            Please only extract relevant information, and format your output as CSV-like data. If any information is missing or not mentioned, leave the field blank.
                            
                            Example Output:
                            "2024-09-04T17:16:45Z, hailong, abc@companya.com, companyA, https://companyA.com, AI research, Nvidia GTX 4090, 100-200, GPT-3, Day: 70%, Night: 30%"
                            "2024-09-04T09:23:08Z, Ross, ross@drmworld.ai, drmworld AI, https://drmworld.ai, Nvidia RTX 4090, 100-200, whisper, Day: higher, Night: lower"
                            """
                        }, 
                        {"role": "user", "content": combined_content}
                    ],
                    temperature=0,
                    max_tokens=1000,
                )
                print(completion.choices[0].message.content)



