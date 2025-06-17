from locust import HttpUser, task, between

class APIUser(HttpUser):
    wait_time = between(1, 2)  # Time to wait between requests

    @task
    def quality_assessment(self):
        image_path = "C:/Users/erraheln/Desktop/iqa/Document-Quality-API/tests/test_api/sample_image.jpg"
        with open(image_path, "rb") as f:
            response = self.client.post(
                "/quality-assessment/",
                files={"image": ("sample_image.jpg", f, "image/jpeg")}
            )
            # Print response status and body for debugging
            print(f"Response Status Code: {response.status_code}")
            print(f"Response Body: {response.text}")
            assert response.status_code == 200


# tesr cm : 
# locust -f locust_test.py --host=http://localhost:8000