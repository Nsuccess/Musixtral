#!/usr/bin/env python3
"""
Test script for MusicToolkit MCP Server
"""

import json
import subprocess
import sys

def test_mcp_server():
    """Test the MCP server by sending JSON-RPC requests"""
    
    # Test 1: Initialize the server
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "1.0"}
        }
    }
    
    print("🧪 Testing MCP Server Initialization...")
    result = send_request(init_request)
    if result and "result" in result:
        print("✅ Server initialized successfully")
        print(f"   Server: {result['result']['serverInfo']['name']}")
        print(f"   Version: {result['result']['serverInfo']['version']}")
    else:
        print("❌ Server initialization failed")
        return False
    
    # Test 2: List available tools
    tools_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    
    print("\n🔧 Testing Tools List...")
    result = send_request(tools_request)
    if result and "result" in result:
        tools = result['result']['tools']
        print(f"✅ Found {len(tools)} tools:")
        for tool in tools:
            print(f"   • {tool['name']}: {tool['description']}")
    else:
        print("❌ Failed to list tools")
        return False
    
    # Test 3: List available resources
    resources_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "resources/list",
        "params": {}
    }
    
    print("\n📦 Testing Resources List...")
    result = send_request(resources_request)
    if result and "result" in result:
        resources = result['result']['resources']
        print(f"✅ Found {len(resources)} resources:")
        for resource in resources:
            print(f"   • {resource['name']}: {resource['description']}")
    else:
        print("❌ Failed to list resources")
    
    # Test 4: List available prompts
    prompts_request = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "prompts/list",
        "params": {}
    }
    
    print("\n💬 Testing Prompts List...")
    result = send_request(prompts_request)
    if result and "result" in result:
        prompts = result['result']['prompts']
        print(f"✅ Found {len(prompts)} prompts:")
        for prompt in prompts:
            print(f"   • {prompt['name']}: {prompt['description']}")
    else:
        print("❌ Failed to list prompts")
    
    print("\n🎉 MCP Server test completed successfully!")
    return True

def send_request(request):
    """Send a JSON-RPC request to the MCP server"""
    try:
        # Convert request to JSON string
        request_json = json.dumps(request)
        
        # Run the server with the request
        process = subprocess.Popen(
            ["uv", "run", "python", "music_toolkit_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send request and get response
        stdout, stderr = process.communicate(input=request_json)
        
        # Parse the JSON response (skip the ASCII art and logs)
        lines = stdout.strip().split('\n')
        for line in lines:
            if line.startswith('{"jsonrpc"'):
                return json.loads(line)
        
        return None
        
    except Exception as e:
        print(f"Error sending request: {e}")
        return None

if __name__ == "__main__":
    test_mcp_server()
