# Copyright 2013 10gen, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Test deprecated client classes Connection and ReplicaSetConnection."""


import sys
import unittest
from bson import ObjectId

sys.path[0:0] = [""]

import pymongo
from pymongo.connection import Connection
from pymongo.replica_set_connection import ReplicaSetConnection
from pymongo.errors import ConfigurationError

from test.test_replica_set_client import TestReplicaSetClientBase
from test.test_client import host, port


class TestConnection(unittest.TestCase):
    def test_connection(self):
        c = Connection(host, port)
        self.assertTrue(c.auto_start_request)
        self.assertFalse(c.slave_okay)
        self.assertFalse(c.safe)
        self.assertEqual({}, c.get_lasterror_options())

        # Connection's writes are unacknowledged by default
        doc = {"_id": ObjectId()}
        coll = c.pymongo_test.write_concern_test
        coll.drop()
        coll.insert(doc)
        coll.insert(doc)

        c = Connection("mongodb://%s:%s/?safe=true" % (host, port))
        self.assertTrue(c.safe)

        # Connection's network_timeout argument is translated into
        # socketTimeoutMS
        self.assertEqual(123, Connection(
            host, port, network_timeout=123)._MongoClient__net_timeout)

        for network_timeout in 'foo', 0, -1:
            self.assertRaises(ConfigurationError,
                Connection, host, port, network_timeout=network_timeout)

    def test_connection_alias(self):
        # Testing that pymongo module imports connection.Connection
        self.assertEqual(Connection, pymongo.Connection)


class TestReplicaSetConnection(TestReplicaSetClientBase):
    def test_replica_set_connection(self):
        c = ReplicaSetConnection(host, port, replicaSet=self.name)
        self.assertTrue(c.auto_start_request)
        self.assertFalse(c.slave_okay)
        self.assertFalse(c.safe)
        self.assertEqual({}, c.get_lasterror_options())

        # ReplicaSetConnection's writes are unacknowledged by default
        doc = {"_id": ObjectId()}
        coll = c.pymongo_test.write_concern_test
        coll.drop()
        coll.insert(doc)
        coll.insert(doc)

        c = ReplicaSetConnection("mongodb://%s:%s/?replicaSet=%s&safe=true" % (
            host, port, self.name))

        self.assertTrue(c.safe)

        # ReplicaSetConnection's network_timeout argument is translated into
        # socketTimeoutMS
        self.assertEqual(123, ReplicaSetConnection(
            host, port, replicaSet=self.name, network_timeout=123
        )._MongoReplicaSetClient__net_timeout)

        for network_timeout in 'foo', 0, -1:
            self.assertRaises(ConfigurationError,
                ReplicaSetConnection, host, port, replicaSet=self.name,
                network_timeout=network_timeout)

    def test_replica_set_connection_alias(self):
        # Testing that pymongo module imports ReplicaSetConnection
        self.assertEqual(ReplicaSetConnection, pymongo.ReplicaSetConnection)

