import pytest


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self, client, reset_activities):
        """Test successfully unregistering from an activity"""
        email = "michael@mergington.edu"  # Already in Chess Club
        response = client.delete(
            f"/activities/Chess%20Club/unregister?email={email}"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert "Chess Club" in data["message"]

    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes participant from activity"""
        email = "michael@mergington.edu"
        response = client.delete(
            f"/activities/Chess%20Club/unregister?email={email}"
        )
        assert response.status_code == 200
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities["Chess Club"]["participants"]

    def test_unregister_activity_not_found(self, client, reset_activities):
        """Test unregistering from non-existent activity"""
        response = client.delete(
            "/activities/Nonexistent%20Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_not_registered(self, client, reset_activities):
        """Test that unregister fails if student is not registered"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]

    def test_unregister_then_rejoin(self, client, reset_activities):
        """Test that student can unregister and then sign up again"""
        email = "sarah@mergington.edu"  # Already in Tennis Club
        
        # First unregister
        response1 = client.delete(
            f"/activities/Tennis%20Club/unregister?email={email}"
        )
        assert response1.status_code == 200
        
        # Verify removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities["Tennis Club"]["participants"]
        
        # Now sign up again
        response2 = client.post(
            f"/activities/Tennis%20Club/signup?email={email}"
        )
        assert response2.status_code == 200
        
        # Verify re-added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities["Tennis Club"]["participants"]

    def test_unregister_one_activity_doesnt_affect_others(self, client, reset_activities):
        """Test that unregistering from one activity doesn't affect other registrations"""
        email = "test@mergington.edu"
        
        # Sign up for two activities
        client.post(f"/activities/Chess%20Club/signup?email={email}")
        client.post(f"/activities/Basketball%20Team/signup?email={email}")
        
        # Unregister from Chess Club
        response = client.delete(
            f"/activities/Chess%20Club/unregister?email={email}"
        )
        assert response.status_code == 200
        
        # Verify removed from Chess Club but still in Basketball Team
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities["Chess Club"]["participants"]
        assert email in activities["Basketball Team"]["participants"]

    def test_unregister_with_multiple_participants(self, client, reset_activities):
        """Test unregistering one participant from an activity with multiple participants"""
        email_to_remove = "michael@mergington.edu"
        email_to_keep = "daniel@mergington.edu"
        
        # Unregister one
        response = client.delete(
            f"/activities/Chess%20Club/unregister?email={email_to_remove}"
        )
        assert response.status_code == 200
        
        # Verify only the specified participant was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email_to_remove not in activities["Chess Club"]["participants"]
        assert email_to_keep in activities["Chess Club"]["participants"]
