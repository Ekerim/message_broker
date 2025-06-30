# Copyright (c) 2025 Your Name
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

import threading
import queue
import logging
import time
import re
import inspect

from typing import Dict, Set, Callable

class MessageBroker:
    _instance = None
    
    def __new__(cls, config=None, singleton=True):
        if singleton:
            # Standard singleton behavior
            if cls._instance is None:
                cls._instance = super(MessageBroker, cls).__new__(cls)
                cls._instance._initialize(config)
            return cls._instance
        else:
            # Create new instance for testing
            instance = super(MessageBroker, cls).__new__(cls)
            instance._initialize(config)
            return instance
        
    def _initialize(self, config=None):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        self.logger.debug(f"Message Broker Initializing. (Client ID: {self.__class__.__module__}.{id(self)})")

        self._running = True
        self.lock = threading.Lock()
        self._wake_event = threading.Event()
        
        # Store configuration
        self._config = config or {}
        self._networking_enabled = self._config.get('network', {}).get('enabled', False)
        
        # Generate unique origin ID for this MessageBroker instance
        self._origin_id = f"{self.__class__.__module__}.{id(self)}"
        self.logger.debug(f"MessageBroker origin ID: {self._origin_id}")
        
        self._topics = {}
        self._message_queue_in = queue.Queue()  # Internal message queue
        
        # Add outgoing message queue for network communication
        if self._networking_enabled:
            self._message_queue_out = queue.Queue()
            self.logger.info("Network messaging enabled")
        else:
            self._message_queue_out = None
            self.logger.info("Network messaging disabled")

        self.logger.info(f"Message Broker Initialized. (Client ID: {self.__class__.__module__}.{id(self)})")
        
        # Start message processing thread
        self.worker = threading.Thread(target=self._process_messages)
        self.worker.daemon = True
        self.worker.start()


    def publish(self, message: dict):
        """Publish a message to the message queue"""
        if not message.get('topic', None) or not message.get('data', None) or not isinstance(message.get('topic'), str):
            self.logger.error("Invalid message format. Message discarded.")
            self.logger.debug(f"\n{message}")
            return
            
        # Always publish to local queue for local subscribers
        self._message_queue_in.put(message)
        
        # Only send to network if message has no origin (local message)
        if message.get('origin') is None:
            if self._networking_enabled:
                self._message_queue_out.put(message)
                self.logger.debug(f"Local message sent to network queue: {message.get('topic')}")
            
        self._wake_event.set()
        # self.logger.debug(f"Published message to topic {message['topic']}: {message['data']}")


    def subscribe(self, topic: str, callback: Callable, subscriber_id: str | None = None):
        """Subscribe to a topic with a callback function"""
        if subscriber_id is None:
            frame = inspect.currentframe().f_back
            module = inspect.getmodule(frame)
            instance = frame.f_locals.get('self')
            subscriber_id = f"{module.__name__}.{id(instance)}"

        with self.lock:
            if topic not in self._topics:
                self._topics[topic] = {}
            self._topics[topic][subscriber_id] = callback
        self.logger.debug(f"Subscribed to topic {topic} with id {subscriber_id}")


    def unsubscribe(self, topic: str, subscriber_id: str | None = None):
        """Unsubscribe from a topic"""
        if subscriber_id is None:
            frame = inspect.currentframe().f_back
            module = inspect.getmodule(frame)
            instance = frame.f_locals.get('self')
            subscriber_id = f"{module.__name__}.{id(instance)}"

        with self.lock:
            if topic in self._topics and subscriber_id in self._topics[topic]:
                del self._topics[topic][subscriber_id]
        self.logger.debug(f"Unsubscribed from topic {topic} with id {subscriber_id}")


    def _process_messages(self):
        """Process messages from all queues"""

        self.logger.info(f"Message Broker started. (Client ID: {self.__class__.__module__}.{id(self)})")

        while self._running:
            start_time = time.time()
            
            while not self._message_queue_in.empty():
                try:
                    message = self._message_queue_in.get_nowait()
                    
                    msg_topic = message['topic']
                    self.logger.debug(f"Processing message for topic: {msg_topic}")
                    for topic_pattern in self._topics:
                        pattern = topic_pattern.replace('*', '.+?')
                        if re.match(pattern, msg_topic):
                            for callback in self._topics[topic_pattern].values():
                                callback(message['data'])
                    
                    self._message_queue_in.task_done()
                except queue.Empty:
                    break
            
            end_time = time.time()
            self.logger.debug(f"Message broker loop. Execution time: {end_time - start_time:.2f} seconds")
            self._wake_event.clear()
            self._wake_event.wait(timeout=300.0)
            self.logger.debug(f"Message broker woken up after {time.time() - end_time:.2f} seconds")


    def stop(self):
        self.logger.debug(f"Message Broker stopping. (Client ID: {self.__class__.__module__}.{id(self)})")

        self._running = False
        self._wake_event.set()
        if self.worker.is_alive():
            self.worker.join()
            
        # Clear all internal state
        self._topics.clear()
        MessageBroker._instance = None
            
        self.logger.info(f"Message Broker stopped. (Client ID: {self.__class__.__module__}.{id(self)})")
