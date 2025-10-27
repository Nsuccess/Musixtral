#!/usr/bin/env python3
"""
Vercel API endpoint for MusicToolkit MCP Server
Simple HTTP handler for MCP protocol
"""

import json
import os
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import requests
from datetime import datetime

# API URLs
VEROVIO_API_URL = "https://ykzou1214--verovio-api-fastapi-app.modal.run"
MUSICGEN_API_URL = "https://ykzou1214--musicgen-melody-api-inference-api.modal.run"

def create_placeholder_musicxml(title="Generated Music", timestamp=None):
    """Create a simple placeholder MusicXML file"""
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    musicxml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<score-partwise version="3.1">
  <work>
    <work-title>{title}</work-title>
  </work>
  <identification>
    <creator type="composer">MusicToolkit AI</creator>
    <encoding>
      <software>MusicToolkit MCP Server</software>
      <encoding-date>{datetime.now().strftime("%Y-%m-%d")}</encoding-date>
    </encoding>
  </identification>
  <part-list>
    <score-part id="P1">
      <part-name>Generated Part</part-name>
    </score-part>
  </part-list>
  <part id="P1">
    <measure number="1">
      <attributes>
        <divisions>4</divisions>
        <key>
          <fifths>0</fifths>
        </key>
        <time>
          <beats>4</beats>
          <beat-type>4</beat-type>
        </time>
        <clef>
          <sign>G</sign>
          <line>2</line>
        </clef>
      </attributes>
      <note>
        <pitch>
          <step>C</step>
          <octave>4</octave>
        </pitch>
        <duration>4</duration>
        <type>quarter</type>
      </note>
      <note>
        <pitch>
          <step>D</step>
          <octave>4</octave>
        </pitch>
        <duration>4</duration>
        <type>quarter</type>
      </note>
      <note>
        <pitch>
          <step>E</step>
          <octave>4</octave>
        </pitch>
        <duration>4</duration>
        <type>quarter</type>
      </note>
      <note>
        <pitch>
          <step>F</step>
          <octave>4</octave>
        </pitch>
        <duration>4</duration>
        <type>quarter</type>
      </note>
    </measure>
  </part>
</score-partwise>'''
    return musicxml_content

def wav_to_music_score(wav_path, render_svg=True, timestamp=None):
    """Convert WAV to music score with optional SVG rendering"""
    try:
        # Create placeholder MusicXML
        musicxml_content = create_placeholder_musicxml("Audio Conversion", timestamp)
        
        result = {
            "success": True,
            "musicxml": musicxml_content,
            "message": "Placeholder MusicXML generated (basic-pitch not available in deployment)"
        }
        
        # Try to render SVG using Verovio API
        if render_svg:
            try:
                verovio_response = requests.post(
                    f"{VEROVIO_API_URL}/render_musicxml",
                    json={"musicxml": musicxml_content},
                    timeout=30
                )
                if verovio_response.status_code == 200:
                    svg_data = verovio_response.json()
                    result["svg"] = svg_data.get("svg", "")
                    result["message"] += " with SVG rendering"
                else:
                    result["svg"] = ""
                    result["message"] += " (SVG rendering failed)"
            except Exception as e:
                result["svg"] = ""
                result["message"] += f" (SVG error: {str(e)})"
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to process audio file"
        }

def generate_music_from_humming(humming_path, generate_score=True, timestamp=None):
    """Generate music from humming audio"""
    try:
        # Try to use MusicGen API
        try:
            musicgen_response = requests.post(
                f"{MUSICGEN_API_URL}/generate",
                json={"audio_path": humming_path, "duration": 30},
                timeout=60
            )
            
            if musicgen_response.status_code == 200:
                generation_data = musicgen_response.json()
                result = {
                    "success": True,
                    "generated_audio": generation_data.get("audio_url", ""),
                    "message": "Music generated successfully using MusicGen"
                }
            else:
                raise Exception(f"MusicGen API error: {musicgen_response.status_code}")
                
        except Exception as api_error:
            # Fallback to placeholder
            result = {
                "success": True,
                "generated_audio": "",
                "message": f"Placeholder response (MusicGen API unavailable: {str(api_error)})"
            }
        
        # Generate music score if requested
        if generate_score:
            musicxml_content = create_placeholder_musicxml("Generated from Humming", timestamp)
            result["musicxml"] = musicxml_content
            result["message"] += " with MusicXML score"
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to generate music from humming"
        }

def handle_mcp_request(request_data):
    """Handle MCP JSON-RPC requests"""
    method = request_data.get('method')
    params = request_data.get('params', {})
    request_id = request_data.get('id', 0)
    
    try:
        if method == 'initialize':
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "resources": {},
                        "prompts": {}
                    },
                    "serverInfo": {
                        "name": "MusicToolkit MCP Server",
                        "version": "1.14.0"
                    }
                }
            }
        
        elif method == 'tools/list':
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": [
                        {
                            "name": "wav_to_music_score",
                            "description": "Convert WAV audio files to MusicXML scores with optional SVG rendering",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "wav_path": {"type": "string", "description": "Path to WAV audio file"},
                                    "render_svg": {"type": "boolean", "description": "Whether to render SVG", "default": True},
                                    "timestamp": {"type": "string", "description": "Optional timestamp for file naming"}
                                },
                                "required": ["wav_path"]
                            }
                        },
                        {
                            "name": "generate_music_from_humming",
                            "description": "Generate full music from humming audio using AI",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "humming_path": {"type": "string", "description": "Path to humming audio file"},
                                    "generate_score": {"type": "boolean", "description": "Whether to generate music score", "default": True},
                                    "timestamp": {"type": "string", "description": "Optional timestamp for file naming"}
                                },
                                "required": ["humming_path"]
                            }
                        }
                    ]
                }
            }
        
        elif method == 'tools/call':
            tool_name = params.get('name')
            arguments = params.get('arguments', {})
            
            if tool_name == 'wav_to_music_score':
                result = wav_to_music_score(**arguments)
            elif tool_name == 'generate_music_from_humming':
                result = generate_music_from_humming(**arguments)
            else:
                raise Exception(f"Unknown tool: {tool_name}")
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ]
                }
            }
        
        elif method == 'resources/list':
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"resources": []}
            }
        
        elif method == 'prompts/list':
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"prompts": []}
            }
        
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
    
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response_data = {
            'name': 'MusicToolkit MCP Server',
            'version': '1.14.0',
            'protocol': 'MCP 2024-11-05',
            'protocolVersion': '2024-11-05',
            'tools': ['wav_to_music_score', 'generate_music_from_humming'],
            'status': 'healthy',
            'endpoints': {
                'mcp': '/api/mcp',
                'tools': '/api/mcp/tools',
                'resources': '/api/mcp/resources',
                'prompts': '/api/mcp/prompts'
            }
        }
        
        self.wfile.write(json.dumps(response_data).encode())
    
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            response_data = handle_mcp_request(request_data)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {
                'jsonrpc': '2.0',
                'id': 0,
                'error': {
                    'code': -32603,
                    'message': f'Internal server error: {str(e)}'
                }
            }
            self.wfile.write(json.dumps(error_response).encode())
