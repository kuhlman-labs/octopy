"""
This module is used to make requests through the GitHub GraphQL API.
"""
import os

from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.exceptions import TransportQueryError, TransportServerError


class GraphRequest:  # pylint: disable=too-few-public-methods
    """
    This following methods are used to form requests to the GitHub GraphQL API.
    """

    def __init__(self, graph_api_url=None, api_token=None):
        """
        Initialize the GraphQL client.
        """
        if api_token is None:
            api_token = os.environ.get("API_TOKEN")
            if os.environ.get("API_TOKEN") is None:
                raise GraphRequestError("API_TOKEN environment variable is not set")
        self._headers = {"Authorization": f"Bearer {api_token}"}
        if graph_api_url is None:
            graph_api_url = os.environ.get("GRAPH_API_URL", r"https://api.github.com/graphql")
        headers = {"Authorization": f"Bearer {api_token}"}
        transport = AIOHTTPTransport(
            url=graph_api_url,
            headers=headers,
        )
        self._client = Client(transport=transport, fetch_schema_from_transport=True)

    def _load_query(self, path):
        """
        Load a query from a file.

        Attributes:
            path (str): Relative path to the query file.
        """
        absolute_path = os.path.dirname(__file__)
        relative_path = path
        full_path = os.path.join(absolute_path, relative_path)
        with open(full_path, encoding="utf8") as file:
            return gql(file.read())

    def _execute(self, query, params):
        """
        Execute a query.

        Attributes:
            query (str): GraphQL query.
            params (dict): Query parameters.
        """
        try:
            return self._client.execute(query, variable_values=params)
        except TransportQueryError as errquery:
            raise GraphRequestError(errquery.errors[0].get("message")) from errquery
        except TransportServerError as errserver:
            raise GraphRequestError(
                f"Server responded with a {str(errserver.code)} status code"
            ) from errserver


class GraphRequestError(Exception):
    """
    Exception raised when an error occurs in the GraphRequest.
    """
