import os
import requests
import json

# Get the JFrog Artifactory credentials and folder name from environment variables
username = os.environ.get("JFROG_USERNAME")
password = os.environ.get("JFROG_PASSWORD")
repository = os.environ.get("JFROG_REPOSITORY")
folder = os.environ.get("JFROG_FOLDER")

# Build the JFrog Artifactory search API endpoint URL
api_url = f"https://{repository}.jfrog.io/artifactory/api/search/"

# Find the Docker images that were created 4 weeks ago and never downloaded
aql_query = f'items.find({{"repo":"{repository}",' \
            f'"path":"{folder}",' \
            f'"name":{{"$regex":".*\\.docker.*"}},' \
            f'"created":{{"$lt":"4w"}},' \
            f'"stat.downloads":{{"$eq":0}}}}).' \
            'include("name","created","stat.downloads")'

# Build the headers for the HTTP request
headers = {"Content-Type": "text/plain"}

# Send the HTTP request to Artifactory to execute the AQL query
response = requests.post(api_url + "aql", headers=headers, auth=(username, password), data=aql_query)

# Parse the JSON response from Artifactory to extract the Docker image names and creation dates
images_to_delete = []
for item in response.json()["results"]:
    image_name = item["name"]
    image_created = item["created"]
    image_downloads = item["stat"]["downloads"]
    images_to_delete.append({"name": image_name, "created": image_created, "downloads": image_downloads})

# Delete each Docker image that was created 4 weeks ago and never downloaded using the Artifactory REST API
for image in images_to_delete:
    delete_url = f"https://{repository}.jfrog.io/artifactory/{repository}/{folder}/{image['name']}"
    print(f"Deleting Docker image {image['name']}...")
    response = requests.delete(delete_url, auth=(username, password))
    if response.status_code == 204:
        print(f"Docker image {image['name']} deleted successfully.")
    else:
        print(f"Failed to delete Docker image {image['name']}. Status code: {response.status_code}")

# Find the Docker images that were last downloaded 4 weeks ago
aql_query = f'items.find({{"repo":"{repository}",' \
            f'"path":"{folder}",' \
            f'"name":{{"$regex":".*\\.docker.*"}},' \
            f'"stat.lastDownloaded":{{"$lt":"4w"}}}}).' \
            'include("name","created","stat.lastDownloaded")'

# Send the HTTP request to Artifactory to execute the AQL query
response = requests.post(api_url + "aql", headers=headers, auth=(username, password), data=aql_query)

# Parse the JSON response from Artifactory to extract the Docker image names and last downloaded dates
images_to_delete = []
for item in response.json()["results"]:
    image_name = item["name"]
    image_created = item["created"]
    image_last_downloaded = item["stat"]["lastDownloaded"]
    images_to_delete.append({"name": image_name, "created": image_created, "last_downloaded": image_last_downloaded})

# Delete each Docker image that was last downloaded 4 weeks ago using the Artifactory REST API
for image in images_to_delete:
    delete_url = f"https://{repository}.
