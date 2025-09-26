from django.test import TestCase, Client
from django.http import JsonResponse
from django.db import connection

class GetDescriptionTestCase(TestCase):
    def setUp(self):
        """
        Set up the test database and client for testing.
        """
        self.client = Client()
        
        # Insert mock data into the table for testing
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO perf_mgmt_evaluateyourmgtsetting (factor_type, description) 
                VALUES (%s, %s)
            """, ["Communication and Leadership", "This factor evaluates communication and leadership skills."])

    def test_get_description_success(self):
        """
        Test that the get_description view returns the correct description for a valid factor type.
        """
        response = self.client.get('/get_description', {'factor_type': 'Communication and Leadership'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {'description': "This factor evaluates communication and leadership skills."}
        )

    def test_get_description_not_found(self):
        """
        Test that the get_description view returns an error if the factor type is not found.
        """
        response = self.client.get('/get_description', {'factor_type': 'Nonexistent Factor'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {'error': 'Description not found'}
        )

    def test_get_description_missing_factor_type(self):
        """
        Test that the get_description view returns an error if the factor type parameter is missing.
        """
        response = self.client.get('/get_description')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {'error': 'Factor type is required'}
        )
