import logging
import json
from typing import Any
import aiohttp
from asyncio import TimeoutError
from datetime import (datetime, timedelta, timezone)
from threading import RLock

from homeassistant.util.dt import (now)

from ..const import INTEGRATION_VERSION

from .account import SmolAccount

_LOGGER = logging.getLogger(__name__)

account_query = '''query GetAccount {{
	customer(market: {market}) {{
    holidayMode {{
      config {{
        endDate
      }}
    }}
    subscriptions(orderBy: NEXT_CHARGE_DATE_ASC) {{
      nextChargeScheduledAt,
      product {{
        typeId
        name
        packSize
      }}
    }}
  }}
}}'''

start_holiday_mode_mutation = '''mutation StartHolidayMode {{
  startHolidayMode(input: {{
    endDate: "{end_date}"
    market: {market}
  }}) {{
    ...HolidayMode
    __typename
 }}
}}

fragment HolidayMode on HolidayMode {{
  id
  __typename
}}
'''

end_holiday_mode_mutation = '''mutation EndHolidayMode {{
  endHolidayModeEarly(input: {{
    market: {market}
  }}) {{
    ...HolidayMode
    __typename
  }}
}}

fragment HolidayMode on HolidayMode {{
  id
  __typename
}}

'''


user_agent_value = "bottlecapdave-ha-smol"

integration_context_header = "Ha-Integration-Context"

class ApiException(Exception): ...

class ServerException(ApiException): ...

class TimeoutException(ApiException): ...

class RequestException(ApiException):
  errors: list[str]

  def __init__(self, message: str, errors: list[str]):
    super().__init__(message)
    self.errors = errors

class AuthenticationException(RequestException): ...

def process_graphql_response(data: Any, url: str, request_context: str, ignore_errors: bool, accepted_error_codes: list[str]):
  if ("graphql" in url and "errors" in data and ignore_errors == False):
    msg = f'Errors in request ({url}) ({request_context}): {data["errors"]}'
    errors = list(map(lambda error: error["message"].strip(".,!"), data["errors"]))
    errors_as_string = ', '.join(errors)
    _LOGGER.warning(msg)

    for error in data["errors"]:
      if ("extensions" in error and
          "errorCode" in error["extensions"] and
          error["extensions"]["errorCode"] in ()):
        raise AuthenticationException(f"Authentication failed - {errors_as_string}. See logs for more details.", errors)

      if ("extensions" in error and
          "errorCode" in error["extensions"] and
          error["extensions"]["errorCode"] in accepted_error_codes):
        return None

    raise RequestException(f"Failed - {errors_as_string}. See logs for more details.", errors)
  
  return data

class SmolApiClient:
  _refresh_token_lock = RLock()
  _session_lock = RLock()

  def __init__(self, username: str, password: str, timeout_in_seconds = 20, market = "GB"):
    if (username is None):
      raise Exception('Username is not set')

    if (password is None):
      raise Exception('Password is not set')

    self._username = username
    self._password = password
    self._market = market
    self._base_url = 'https://customer-api.smol.com'

    self._graphql_token = None
    self._graphql_expiration = None

    self._timeout = aiohttp.ClientTimeout(total=None, sock_connect=timeout_in_seconds, sock_read=timeout_in_seconds)
    self._default_headers = { "user-agent": f'{user_agent_value}/{INTEGRATION_VERSION}' }

    self._session = None

  async def async_close(self):
    with self._session_lock:
      if self._session is not None:
        await self._session.close()

  def _create_client_session(self):
    if self._session is not None:
      return self._session
    
    with self._session_lock:
      if self._session is not None:
        return self._session
      
      self._session = aiohttp.ClientSession(headers=self._default_headers, skip_auto_headers=['User-Agent'])
      return self._session

  async def async_refresh_token(self):
    """Refresh user token"""
    if (self._graphql_expiration is not None and (self._graphql_expiration - timedelta(minutes=5)) > now()):
      return

    with self._refresh_token_lock:
      # Check that our token wasn't refreshed while waiting for the lock
      if (self._graphql_expiration is not None and (self._graphql_expiration - timedelta(minutes=5)) > now()):
        return

      try:
        try:
          await self.__async_fetch_token()
        except AuthenticationException:
          if (self._graphql_refresh_token is not None):
            _LOGGER.debug("Failed to refresh auth token using refresh token, attempting to use original API key")
            self._graphql_refresh_token = None
            self._graphql_expiration = None
            
            await self.__async_fetch_token()
          else:
            raise

      except TimeoutError:
        _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
        raise TimeoutException()

  async def __async_fetch_token(self):
    client = self._create_client_session()
    url = 'https://login.smolproducts.com/oauth/token'
    payload = {
      "grant_type": "http://auth0.com/oauth/grant-type/password-realm",
      "client_id": "sp7P3EXkSoOFxZFjvncSLPduD4Kr5kFv",
      "username": self._username,
      "password": self._password,
      "realm": "Username-Password-Authentication",
      "audience": "https://customer-api.smolproducts.com",
      "scope": "openid profile email"
    }
    headers = {}
    async with client.post(url, headers=headers, json=payload) as token_response:
      token_response_body = await self.__async_read_response__(token_response, url)
      if (token_response_body is not None and 
          "access_token" in token_response_body and
          "expires_in" in token_response_body):
        
        self._graphql_token = token_response_body["access_token"]
        self._graphql_expiration = now() + timedelta(seconds=(int(token_response_body["expires_in"])))
      elif (self._graphql_expiration is None or self._graphql_expiration > now()):
        raise AuthenticationException("Failed to retrieve auth token and current token is expired")
      else:
        _LOGGER.error("Failed to retrieve auth token")
    
  async def async_get_account(self) -> SmolAccount | None:
    """Get the user's account"""
    await self.async_refresh_token()

    try:
      client = self._create_client_session()
      url = f'{self._base_url}/v2/graphql'
      # Get account response
      payload = { "query": account_query.format(market=self._market), "variables": { "market": self._market } }
      headers = { "Authorization": f"Bearer {self._graphql_token}" }
      async with client.post(url, json=payload, headers=headers) as account_response:
        account_response_body = await self.__async_read_response__(account_response, url)
        _LOGGER.debug(f'account: {account_response_body}')

        if (account_response_body is not None and 
            "data" in account_response_body and 
            "customer" in account_response_body["data"]):
          return SmolAccount.model_validate(account_response_body["data"]["customer"])
        else:
          _LOGGER.error("Failed to retrieve account")
    
    except TimeoutError:
      _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
      raise TimeoutException()
    
    return None
  
  async def async_start_holiday(self, end_date: datetime) -> SmolAccount | None:
    """Set holiday mode for the user"""
    await self.async_refresh_token()

    try:
      client = self._create_client_session()
      url = f'{self._base_url}/v2/graphql'
      # Get account response
      payload = { "query": start_holiday_mode_mutation.format(end_date=end_date.isoformat(), market=self._market), "variables": { "market": self._market } }
      headers = { "Authorization": f"Bearer {self._graphql_token}" }
      async with client.post(url, json=payload, headers=headers) as account_response:
        account_response_body = await self.__async_read_response__(account_response, url)
        _LOGGER.debug(f'start_holiday response: {account_response_body}')

        if (account_response_body is not None and 
            "data" in account_response_body and 
            "startHolidayMode" in account_response_body["data"]):
          return "id" in account_response_body["data"]["startHolidayMode"]
        else:
          _LOGGER.error("Failed to set holiday mode")
    
    except TimeoutError:
      _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
      raise TimeoutException()
    
    return False
  
  async def async_end_holiday(self) -> SmolAccount | None:
    """End holiday mode for the user"""
    await self.async_refresh_token()

    try:
      client = self._create_client_session()
      url = f'{self._base_url}/v2/graphql'
      # Get account response
      payload = { "query": end_holiday_mode_mutation.format(market=self._market), "variables": { "market": self._market } }
      headers = { "Authorization": f"Bearer {self._graphql_token}" }
      async with client.post(url, json=payload, headers=headers) as account_response:
        account_response_body = await self.__async_read_response__(account_response, url)
        _LOGGER.debug(f'end_holiday response: {account_response_body}')

        if (account_response_body is not None and 
            "data" in account_response_body and 
            "endHolidayModeEarly" in account_response_body["data"]):
          return "id" in account_response_body["data"]["endHolidayModeEarly"]
        else:
          _LOGGER.error("Failed to set holiday mode")
    
    except TimeoutError:
      _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
      raise TimeoutException()
    
    return False

  async def __async_read_response__(self, response, url, ignore_errors = False, accepted_error_codes = []):
    """Reads the response, logging any json errors"""

    request_context = response.request_info.headers[integration_context_header] if integration_context_header in response.request_info.headers else "Unknown"

    text = await response.text()

    if response.status >= 400:
      if response.status >= 500:
        msg = f'Response received - {url} ({request_context}) - DO NOT REPORT - Smol server error ({url}): {response.status}; {text}'
        _LOGGER.warning(msg)
        raise ServerException(msg)
      elif response.status in [401, 403]:
        msg = f'Response received - {url} ({request_context}) - Unauthenticated request: {response.status}; {text}'
        _LOGGER.warning(msg)
        raise AuthenticationException(msg, [])
      elif response.status not in [404]:
        msg = f'Response received - {url} ({request_context}) - Failed to send request: {response.status}; {text}'
        _LOGGER.warning(msg)
        raise RequestException(msg, [])
      
      _LOGGER.info(f"Response received - {url} ({request_context}) - Unexpected response received: {response.status}; {text}")
      return None
    
    _LOGGER.debug(f'Response received - {url} ({request_context}) - Successful response')

    data_as_json = None
    try:
      data_as_json = json.loads(text)
    except:
      raise Exception(f'Failed to extract response json: {url}; {text}')
    
    return process_graphql_response(data_as_json, url, request_context, ignore_errors, accepted_error_codes)
