import requests

username = "vivekcodespace-arch"

url = f"https://api.github.com/users/{username}"

response = requests.get(url)

print(response.status_code)
# print(response.json())