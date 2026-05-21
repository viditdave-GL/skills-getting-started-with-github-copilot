import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestActivitiesEndpoint:
    def test_get_activities_returns_all_activities(self):
        """Test GET /activities returns all activities"""
        # Arrange
        expected_activities = ["Chess Club", "Programming Class"]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert isinstance(data, dict)
        assert all(activity in data for activity in expected_activities)

    def test_get_activities_structure(self):
        """Test activity data structure"""
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        
        # Assert
        assert response.status_code == 200
        assert all(field in activity for field in required_fields)
        assert isinstance(activity["participants"], list)


class TestSignupEndpoint:
    def test_signup_successful(self):
        """Test successful signup"""
        # Arrange
        test_email = "newstudent@example.com"
        activity_name = "Chess Club"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={test_email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]

    def test_signup_duplicate_email_rejected(self):
        """Test duplicate signup is rejected"""
        # Arrange
        test_email = "duplicate@example.com"
        activity_name = "Programming Class"
        
        # Act - First signup
        first_response = client.post(
            f"/activities/{activity_name}/signup?email={test_email}"
        )
        
        # Act - Second signup (should fail)
        second_response = client.post(
            f"/activities/{activity_name}/signup?email={test_email}"
        )
        
        # Assert
        assert first_response.status_code == 200
        assert second_response.status_code == 400
        assert "already signed up" in second_response.json()["detail"]

    def test_signup_activity_not_found(self):
        """Test signup for non-existent activity"""
        # Arrange
        nonexistent_activity = "Fake Activity"
        test_email = "test@example.com"
        
        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup?email={test_email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_adds_participant_to_list(self):
        """Test that signup adds participant to activity"""
        # Arrange
        test_email = "newuser@example.com"
        activity_name = "Drama Club"
        
        # Act
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={test_email}"
        )
        activities_response = client.get("/activities")
        activity_data = activities_response.json()[activity_name]
        
        # Assert
        assert signup_response.status_code == 200
        assert test_email in activity_data["participants"]


class TestUnregisterEndpoint:
    def test_unregister_successful(self):
        """Test successful unregistration"""
        # Arrange
        test_email = "unregister@example.com"
        activity_name = "Robotics Club"
        client.post(f"/activities/{activity_name}/signup?email={test_email}")
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={test_email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

    def test_unregister_removes_participant(self):
        """Test that unregister removes participant from activity"""
        # Arrange
        test_email = "removeuser@example.com"
        activity_name = "Art Studio"
        
        # Act - Sign up
        client.post(f"/activities/{activity_name}/signup?email={test_email}")
        activities_before = client.get("/activities").json()
        
        # Act - Unregister
        client.delete(f"/activities/{activity_name}/unregister?email={test_email}")
        activities_after = client.get("/activities").json()
        
        # Assert
        assert test_email in activities_before[activity_name]["participants"]
        assert test_email not in activities_after[activity_name]["participants"]

    def test_unregister_not_registered_email(self):
        """Test unregister fails for non-registered email"""
        # Arrange
        activity_name = "Chess Club"
        unregistered_email = "notregistered@example.com"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={unregistered_email}"
        )
        
        # Assert
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]

    def test_unregister_activity_not_found(self):
        """Test unregister fails for non-existent activity"""
        # Arrange
        nonexistent_activity = "Fake Activity"
        test_email = "test@example.com"
        
        # Act
        response = client.delete(
            f"/activities/{nonexistent_activity}/unregister?email={test_email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestRootEndpoint:
    def test_root_redirects_to_static_html(self):
        """Test root path redirects to static/index.html"""
        # Arrange
        expected_location = "/static/index.html"
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert expected_location in response.headers["location"]
