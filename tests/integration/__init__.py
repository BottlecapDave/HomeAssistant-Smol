import logging
import os

logging.getLogger().setLevel(logging.DEBUG)

class TestContext:
  username: str
  password: str

  def __init__(self, username, password):
    self.username = username
    self.password = password

def get_test_context():
  username = os.environ["SMOL_USERNAME"]
  if (username is None):
      raise Exception("SMOL_USERNAME must be set")

  password = os.environ["SMOL_PASSWORD"]
  if (password is None):
      raise Exception("SMOL_PASSWORD must be set")
  
  return TestContext(username, password)