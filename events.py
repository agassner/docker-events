#!/usr/bin/env python

import redis
import os

from docker.client import Client


class Redis():

    def __init__(self, host, port=6379, db=0):
        self.client = redis.StrictRedis(host=host, port=port, db=db)

    def get_client(self):
        return self.client

    def get(self, key):
        return self.client.get(key)

    def set(self, key, event):
        self.client.set(key, event)


class DockerDaemon():

    def __init__(self, db):
        self.client = Client()
        self.db = db

    def get_events(self):
        events = self.client.events(decode=True)

        for event in events:
            if event:
                if event.get('status') in ['start', 'die']:
                    self.send_container_status(event)

    def send_container_status(self, event):
        event['container'] = self.get_container(event.get('id'))
        key = '%s_%s' % (event.get('id'), event.get('status'))
        self.db.set(key, event)

    def get_container(self, id):
        return self.client.inspect_container(id)


r = Redis(os.environ.get('REDIS_HOST'))
dd = DockerDaemon(r)
dd.get_events()
