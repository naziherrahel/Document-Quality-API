from locust import HttpUser, task, between
import os

class APIUser(HttpUser):
    wait_time = between(1, 2)  # Time to wait between requests

    @task
    def quality_assessment(self):
        image_path = "C:/Users/erraheln/Desktop/iqa/Document-Quality-API/tests/test_api/sample_image.jpg"
        
        with open(image_path, "rb") as f:
            response = self.client.post(
                "/quality-assessment/",  # Single image endpoint
                files={"image": ("sample_image.jpg", f, "image/jpeg")}
            )
            # Print response status and body for debugging
            print(f"Response Status Code: {response.status_code}")
            print(f"Response Body: {response.text}")
            
            # Assert the response status code and check for expected fields in the response
            if response.status_code != 200:
                print(f"Error: Received status code {response.status_code}")
                print(f"Response Body: {response.text}")  # Print body for more information

            assert response.status_code == 200, f"Expected 200, but got {response.status_code}. Body: {response.text}"
            assert "doc_type" in response.json()  # Check if the response contains the expected field doc_type
            assert "global_score" in response.json()  # You can add more checks here based on expected keys