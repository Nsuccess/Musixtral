#!/usr/bin/env python3
"""
Example usage of MusicToolkit MCP Server
Demonstrates how to interact with the server programmatically
"""

import json
import subprocess
import tempfile
import os

class MusicToolkitMCPClient:
    """Simple MCP client for testing MusicToolkit server"""
    
    def __init__(self):
        self.request_id = 0
        self.initialized = False
    
    def _send_request(self, method, params=None):
        """Send a JSON-RPC request to the MCP server"""
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params or {}
        }
        
        try:
            request_json = json.dumps(request)
            process = subprocess.Popen(
                ["uv", "run", "python", "music_toolkit_server.py"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.path.dirname(__file__)
            )
            
            stdout, stderr = process.communicate(input=request_json)
            
            # Find the JSON response in the output
            lines = stdout.strip().split('\n')
            for line in lines:
                if line.startswith('{"jsonrpc"'):
                    return json.loads(line)
            
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def initialize(self):
        """Initialize the MCP server"""
        response = self._send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "MusicToolkit Example Client", "version": "1.0"}
        })
        
        if response and "result" in response:
            self.initialized = True
            return response["result"]
        return None
    
    def list_tools(self):
        """List available tools"""
        if not self.initialized:
            return None
        return self._send_request("tools/list")
    
    def call_tool(self, tool_name, arguments):
        """Call a specific tool"""
        if not self.initialized:
            return None
        return self._send_request("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })

def demo_wav_to_score():
    """Demo: Convert WAV to music score"""
    print("🎼 Demo: WAV to Music Score")
    print("=" * 50)
    
    client = MusicToolkitMCPClient()
    
    # Initialize
    init_result = client.initialize()
    if not init_result:
        print("❌ Failed to initialize MCP server")
        return
    
    print(f"✅ Initialized: {init_result['serverInfo']['name']}")
    
    # Create a dummy WAV file path for demonstration
    dummy_wav = "/path/to/your/audio.wav"
    
    # Call the wav_to_music_score tool
    print(f"\n🎵 Converting WAV file: {dummy_wav}")
    result = client.call_tool("wav_to_music_score", {
        "wav_file_path": dummy_wav,
        "render_svg": True
    })
    
    if result and "result" in result:
        print("✅ Tool call successful:")
        print(result["result"]["content"][0]["text"])
    else:
        print("❌ Tool call failed")
        if result and "error" in result:
            print(f"Error: {result['error']}")

def demo_generate_from_humming():
    """Demo: Generate music from humming"""
    print("\n🎤 Demo: Generate Music from Humming")
    print("=" * 50)
    
    client = MusicToolkitMCPClient()
    
    # Initialize
    init_result = client.initialize()
    if not init_result:
        print("❌ Failed to initialize MCP server")
        return
    
    print(f"✅ Initialized: {init_result['serverInfo']['name']}")
    
    # Create a dummy humming file path for demonstration
    dummy_humming = "/path/to/your/humming.wav"
    
    # Call the generate_music_from_humming tool
    print(f"\n🎵 Generating music from: {dummy_humming}")
    result = client.call_tool("generate_music_from_humming", {
        "humming_file_path": dummy_humming,
        "style_prompt": "upbeat electronic dance music with synthesizers",
        "generate_score": True
    })
    
    if result and "result" in result:
        print("✅ Tool call successful:")
        print(result["result"]["content"][0]["text"])
    else:
        print("❌ Tool call failed")
        if result and "error" in result:
            print(f"Error: {result['error']}")

def show_server_info():
    """Show server capabilities and available tools"""
    print("📋 MusicToolkit MCP Server Information")
    print("=" * 50)
    
    client = MusicToolkitMCPClient()
    
    # Initialize
    init_result = client.initialize()
    if not init_result:
        print("❌ Failed to initialize MCP server")
        return
    
    print(f"Server Name: {init_result['serverInfo']['name']}")
    print(f"Server Version: {init_result['serverInfo']['version']}")
    print(f"Protocol Version: {init_result['protocolVersion']}")
    
    # Show capabilities
    capabilities = init_result['capabilities']
    print(f"\nCapabilities:")
    print(f"  • Tools: {'✅' if 'tools' in capabilities else '❌'}")
    print(f"  • Resources: {'✅' if 'resources' in capabilities else '❌'}")
    print(f"  • Prompts: {'✅' if 'prompts' in capabilities else '❌'}")

if __name__ == "__main__":
    print("🎵 MusicToolkit MCP Server - Example Usage")
    print("=" * 60)
    
    # Show server information
    show_server_info()
    
    # Demo WAV to score conversion
    demo_wav_to_score()
    
    # Demo music generation from humming
    demo_generate_from_humming()
    
    print("\n" + "=" * 60)
    print("💡 To use with real audio files:")
    print("1. Replace dummy file paths with actual WAV files")
    print("2. Ensure the MusicToolkit server is properly configured")
    print("3. Check that external APIs are accessible")
    print("\n🚀 Ready to integrate with Le Chat or other MCP clients!")
