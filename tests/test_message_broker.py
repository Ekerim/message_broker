# Copyright (c) 2025 Fredrik Larsson
# 
# This file is part of the Message Broker library.
# 
# The Message Broker library is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# The Message Broker library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with this library. If not, see <https://www.gnu.org/licenses/>.

import unittest
from message_broker import MessageBroker

class TestMessageBroker(unittest.TestCase):
    def test_publish_and_subscribe(self):
        broker = MessageBroker()
        broker.subscribe("topic", lambda msg: self.assertEqual(msg, "test message"))
        broker.publish("topic", "test message")

if __name__ == "__main__":
    unittest.main()
