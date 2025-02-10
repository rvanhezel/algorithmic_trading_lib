import requests
import logging
from typing import Optional, Any


class RestAPI:

    def __init__(self) -> None:
        """
        Initialize the RestAPI class with a base URL and access key.
        :param base_url: The base URL for the API.
        :param access_key: The access key for authentication.
        """
        self._base_url: str = None
        self._access_key: str = None
        self._default_headers: dict[str, str] = {
            "Authorization": f"Bearer {self.access_key}",
            "Content-Type": "application/json",
        }

    @property
    def base_url(self) -> str:
        return self._base_url
    
    @property
    def access_key(self) -> str:
        return self._access_key
    
    @property
    def default_headers(self) -> dict[str, str]:
        return self._default_headers
    
    @base_url.setter
    def base_url(self, value: str) -> None:
        self._base_url = value.rstrip("/")

    @access_key.setter
    def access_key(self, value: str) -> None:
        self._access_key = value
        self._default_headers["Authorization"] = f"Bearer {value}"

    def get(self, endpoint: str = None, headers: Optional[dict[str, str]] = None, params: Optional[dict[str, Any]] = None) -> Optional[dict[str, Any]]:
        """
        Perform a GET request.
        :param endpoint: The API endpoint (e.g., "/resource").
        :param headers: Optional additional headers for the request.
        :param params: Optional query parameters for the request.
        :return: Parsed JSON response if successful, None otherwise.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}" if endpoint else self.base_url
        try:
            combined_headers = {**self.default_headers, **(headers or {})}
            response = requests.get(url, headers=combined_headers, params=params)
            response.raise_for_status()
            
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"GET request failed: {e}")
            return None

    def post(self, endpoint: str, data: Optional[dict[str, Any]] = None, headers: Optional[dict[str, str]] = None) -> Optional[dict[str, Any]]:
        """
        Perform a POST request.
        :param endpoint: The API endpoint (e.g., "/resource").
        :param data: The data to send in the request body (usually a dict).
        :param headers: Optional additional headers for the request.
        :return: Parsed JSON response if successful, None otherwise.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            combined_headers = {**self.default_headers, **(headers or {})}
            response = requests.post(url, json=data, headers=combined_headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"POST request failed: {e}")
            return None

    def put(self, endpoint: str, data: Optional[dict[str, Any]] = None, headers: Optional[dict[str, str]] = None) -> Optional[dict[str, Any]]:
        """
        Perform a PUT request.
        :param endpoint: The API endpoint (e.g., "/resource").
        :param data: The data to update in the request body (usually a dict).
        :param headers: Optional additional headers for the request.
        :return: Parsed JSON response if successful, None otherwise.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            combined_headers = {**self.default_headers, **(headers or {})}
            response = requests.put(url, json=data, headers=combined_headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"PUT request failed: {e}")
            return None

    def delete(self, endpoint: str, headers: Optional[dict[str, str]] = None) -> Optional[dict[str, Any]]:
        """
        Perform a DELETE request.
        :param endpoint: The API endpoint (e.g., "/resource").
        :param headers: Optional additional headers for the request.
        :return: Parsed JSON response or a success message if successful, None otherwise.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            combined_headers = {**self.default_headers, **(headers or {})}
            response = requests.delete(url, headers=combined_headers)
            response.raise_for_status()
            if response.status_code == 204:
                return {"message": "Resource deleted successfully"}
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"DELETE request failed: {e}")
            return None
        
    # def batch_get()
    # fun to make one api call with multiple endpoints and multiple arguments