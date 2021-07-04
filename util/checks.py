import json
import os


def is_dev(ctx):
  with open(f"{os.path.dirname(__file__)}") as f:
    conf = json.load(f)
  return str(ctx.author.id) in conf["devs"].values()