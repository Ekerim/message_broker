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

import threading
import logging
import json
from typing import Dict, Any, Optional

from twisted.internet import reactor, protocol, endpoints
from twisted.python import log


class NetworkServer:
    """
    Handles network communication for the MessageBroker using Twisted.
    Runs the Twisted reactor in a separate thread to avoid blocking.
    """
    
    def __init__(self, message_broker, config: Dict[str, Any]):
        self.logger = logging.getLogger(__name__)
        self.message_broker = message_broker
        self.config = config.get('network', {})
        
        # Network configuration
        self.host = self.config.get('host', 'localhost')
        self.port = self.config.get('port', 8080)
        self.secret = self.config.get('secret', '')
        
        # Threading
        self._reactor_thread = None
        self._running = False
        
        self.logger.info(f"NetworkServer initialized for {self.host}:{self.port}")
    
    def start(self):
        """Start the network server in a separate thread"""
        if self._running:
            self.logger.warning("NetworkServer already running")
            return
            
        self._running = True
        self._reactor_thread = threading.Thread(target=self._run_reactor, daemon=True)
        self._reactor_thread.start()
        self.logger.info("NetworkServer started")
    
    def stop(self):
        """Stop the network server"""
        if not self._running:
            return
            
        self._running = False
        if reactor.running:
            reactor.callFromThread(reactor.stop)
        
        if self._reactor_thread and self._reactor_thread.is_alive():
            self._reactor_thread.join(timeout=5.0)
            
        self.logger.info("NetworkServer stopped")
    
    def _run_reactor(self):
        """Run the Twisted reactor in this thread"""
        try:
            # TODO: Set up protocol factory and endpoint
            # TODO: Start monitoring outgoing message queue
            # TODO: Set up authentication
            
            self.logger.info("Twisted reactor starting")
            reactor.run(installSignalHandlers=False)
            self.logger.info("Twisted reactor stopped")
            
        except Exception as e:
            self.logger.error(f"Error in reactor thread: {e}")
        finally:
            self._running = False
