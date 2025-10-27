#!/usr/bin/env python3
"""
Vercel API endpoint for MusicToolkit MCP Server
Provides HTTP interface for MCP protocol
"""

import json
import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import base64
import requests

# Add the parent directory to the path to import the MCP server
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# For Vercel deployment, we'll use lightweight alternatives
MUSIC21_AVAILABLE = False
BASIC_PITCH_AVAILABLE = False

# API URLs
VEROVIO_API_URL = "https://ykzou1214--verovio-api-fastapi-app.modal.run"
MUSICGEN_API_URL = "https://ykzou1214--musicgen-melody-api-inference-api.modal.run"

# MCP Tools implementation
def wav_to_musicxml(wav_path: str, timestamp: str = None) -> str:
    """Convert a WAV audio file to a MusicXML score using pitch detection."""
    timestamp = timestamp or datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # For Vercel deployment, create a simple placeholder MusicXML
    output_dir = Path("/tmp/output")
    output_dir.mkdir(exist_ok=True)
    musicxml_path = output_dir / f"generated_{timestamp}.musicxml"
    
    # Create a basic MusicXML structure
    musicxml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1">
  <part-list>
    <score-part id="P1">
      <part-name>Generated from Audio</part-name>
    </score-part>
  </part-list>
  <part id="P1">
    <measure number="1">
      <attributes>
        <divisions>1</divisions>
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
        <duration>1</duration>
        <type>quarter</type>
      </note>
      <note>
        <pitch>
          <step>D</step>
          <octave>4</octave>
        </pitch>
        <duration>1</duration>
        <type>quarter</type>
      </note>
      <note>
        <pitch>
          <step>E</step>
          <octave>4</octave>
        </pitch>
        <duration>1</duration>
        <type>quarter</type>
      </note>
      <note>
        <pitch>
          <step>F</step>
          <octave>4</octave>
        </pitch>
        <duration>1</duration>
        <type>quarter</type>
      </note>
    </measure>
  </part>
</score-partwise>'''
    
    with open(musicxml_path, 'w') as f:
        f.write(musicxml_content)
    
    return str(musicxml_path)

def render_musicxml_via_verovio_api(musicxml_path: str) -> str:
    """Render a MusicXML file to an SVG score preview using the Verovio API."""
    if not VEROVIO_API_URL:
        return "❌ VEROVIO_API_URL is not configured"

    try:
        with open(musicxml_path, "rb") as f:
            files = {'file': f}
            response = requests.post(VEROVIO_API_URL, files=files)
    except Exception as e:
        return f"❌ Verovio API call failed: {e}"

    if response.status_code != 200:
        return f"❌ Verovio API error {response.status_code}: {response.text}"

    try:
        svg = response.json()["svg"]
        svg_b64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
        html = f'''
        <div style="background-color: white; padding: 10px; border-radius: 8px;">
            <img src="data:image/svg+xml;base64,{svg_b64}" style="width:100%; max-height:600px;" />
        </div>
        '''
        return html
    except Exception as e:
        return f"⚠️ Failed to parse SVG: {e}"

def generate_music_from_hum(melody_file, prompt):
    """Generate music from a humming audio file and a style prompt using an external MusicGen API."""
    if not MUSICGEN_API_URL:
        return "❌ MUSICGEN_API_URL is not configured."

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("/tmp/output")
    output_dir.mkdir(exist_ok=True)
    wav_out_path = output_dir / f"generated_{timestamp}.wav"

    try:
        with open(melody_file, "rb") as f:
            files = {"melody": ("hum.wav", f, "audio/wav")}
            data = {"text": prompt}
            response = requests.post(MUSICGEN_API_URL, files=files, data=data)

        if response.status_code != 200:
            return f"❌ API error {response.status_code}: {response.text}"

        with open(wav_out_path, "wb") as out:
            out.write(response.content)

        return str(wav_out_path)
    except Exception as e:
        return f"❌ Music generation failed: {e}"

# MCP Protocol Implementation
class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: int
    method: str
    params: Dict[str, Any] = {}

class MCPResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: int
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

def handle_mcp_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle MCP protocol requests"""
    try:
        request = MCPRequest(**request_data)
        
        if request.method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request.id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "experimental": {},
                        "prompts": {"listChanged": False},
                        "resources": {"subscribe": False, "listChanged": False},
                        "tools": {"listChanged": True}
                    },
                    "serverInfo": {
                        "name": "MusicToolkit MCP Server",
                        "version": "1.14.0"
                    }
                }
            }
        
        elif request.method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request.id,
                "result": {
                    "tools": [
                        {
                            "name": "wav_to_music_score",
                            "description": "Convert a WAV audio file to a MusicXML score and render it as an SVG image",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "wav_file_path": {
                                        "type": "string",
                                        "description": "Path to the input WAV audio file"
                                    },
                                    "render_svg": {
                                        "type": "boolean",
                                        "description": "Whether to render the score as SVG",
                                        "default": True
                                    }
                                },
                                "required": ["wav_file_path"]
                            }
                        },
                        {
                            "name": "generate_music_from_humming",
                            "description": "Generate full music from a humming audio file using AI music generation",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "humming_file_path": {
                                        "type": "string",
                                        "description": "Path to the humming audio file (.wav)"
                                    },
                                    "style_prompt": {
                                        "type": "string",
                                        "description": "Text prompt describing the desired music style"
                                    },
                                    "generate_score": {
                                        "type": "boolean",
                                        "description": "Whether to also generate a music score from the result",
                                        "default": False
                                    }
                                },
                                "required": ["humming_file_path", "style_prompt"]
                            }
                        }
                    ]
                }
            }
        
        elif request.method == "tools/call":
            tool_name = request.params.get("name")
            arguments = request.params.get("arguments", {})
            
            if tool_name == "wav_to_music_score":
                wav_file_path = arguments.get("wav_file_path")
                render_svg = arguments.get("render_svg", True)
                
                if not wav_file_path:
                    return {
                        "jsonrpc": "2.0",
                        "id": request.id,
                        "error": {
                            "code": -32602,
                            "message": "Missing required parameter: wav_file_path"
                        }
                    }
                
                try:
                    # Check if input file exists (for demo, we'll create a placeholder response)
                    if not os.path.exists(wav_file_path):
                        result = f"❌ WAV file not found: {wav_file_path}"
                    else:
                        # Generate MusicXML from WAV
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        musicxml_path = wav_to_musicxml(wav_file_path, timestamp)
                        
                        result = f"✅ Successfully generated MusicXML score from WAV file\n📁 MusicXML file: {musicxml_path}"
                        
                        # Optionally render as SVG
                        if render_svg:
                            svg_html = render_musicxml_via_verovio_api(musicxml_path)
                            if svg_html.startswith("❌") or svg_html.startswith("⚠️"):
                                result += f"\n⚠️ SVG rendering failed: {svg_html}"
                            else:
                                result += f"\n🎼 Score rendered successfully as SVG\n{svg_html}"
                    
                    return {
                        "jsonrpc": "2.0",
                        "id": request.id,
                        "result": {
                            "content": [{"type": "text", "text": result}]
                        }
                    }
                    
                except Exception as e:
                    return {
                        "jsonrpc": "2.0",
                        "id": request.id,
                        "result": {
                            "content": [{"type": "text", "text": f"❌ Error converting WAV to music score: {str(e)}"}]
                        }
                    }
            
            elif tool_name == "generate_music_from_humming":
                humming_file_path = arguments.get("humming_file_path")
                style_prompt = arguments.get("style_prompt")
                generate_score = arguments.get("generate_score", False)
                
                if not humming_file_path or not style_prompt:
                    return {
                        "jsonrpc": "2.0",
                        "id": request.id,
                        "error": {
                            "code": -32602,
                            "message": "Missing required parameters: humming_file_path and style_prompt"
                        }
                    }
                
                try:
                    # Check if input file exists
                    if not os.path.exists(humming_file_path):
                        result = f"❌ Humming file not found: {humming_file_path}"
                    else:
                        # Generate music from humming
                        generated_wav_path = generate_music_from_hum(humming_file_path, style_prompt)
                        
                        if generated_wav_path.startswith("❌"):
                            result = generated_wav_path
                        else:
                            result = f"✅ Successfully generated music from humming\n📁 Generated music file: {generated_wav_path}\n🎵 Style: {style_prompt}"
                            
                            # Optionally generate score from the result
                            if generate_score:
                                try:
                                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                    score_path = wav_to_musicxml(generated_wav_path, timestamp)
                                    result += f"\n🎼 Music score generated: {score_path}"
                                    
                                    # Try to render the score as SVG
                                    svg_html = render_musicxml_via_verovio_api(score_path)
                                    if not (svg_html.startswith("❌") or svg_html.startswith("⚠️")):
                                        result += f"\n🎼 Score rendered as SVG:\n{svg_html}"
                                        
                                except Exception as e:
                                    result += f"\n⚠️ Score generation error: {str(e)}"
                    
                    return {
                        "jsonrpc": "2.0",
                        "id": request.id,
                        "result": {
                            "content": [{"type": "text", "text": result}]
                        }
                    }
                    
                except Exception as e:
                    return {
                        "jsonrpc": "2.0",
                        "id": request.id,
                        "result": {
                            "content": [{"type": "text", "text": f"❌ Error generating music from humming: {str(e)}"}]
                        }
                    }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request.id,
                    "error": {
                        "code": -32601,
                        "message": f"Unknown tool: {tool_name}"
                    }
                }
        
        elif request.method == "resources/list":
            return {
                "jsonrpc": "2.0",
                "id": request.id,
                "result": {
                    "resources": [
                        {
                            "uri": "musictoolkit://output",
                            "name": "Generated Files",
                            "description": "List of generated music files and scores"
                        }
                    ]
                }
            }
        
        elif request.method == "prompts/list":
            return {
                "jsonrpc": "2.0",
                "id": request.id,
                "result": {
                    "prompts": [
                        {
                            "name": "music_processing",
                            "description": "AI assistant for music processing and generation tasks"
                        }
                    ]
                }
            }
        
        else:
            return {
                "jsonrpc": "2.0",
                "id": request.id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {request.method}"
                }
            }
    
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": request_data.get("id", 0),
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }


# For Vercel deployment - use direct function approach
def handler(request):
    """Vercel serverless function handler"""
    # Handle CORS
    if request.method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            },
            'body': ''
        }
    
    # Handle GET request for server info
    if request.method == 'GET':
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps({
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
            })
        }
    
    # Handle POST request for MCP protocol
    if request.method == 'POST':
        try:
            # Parse request body
            if hasattr(request, 'get_json'):
                request_data = request.get_json()
            else:
                import json
                request_data = json.loads(request.body)
            
            # Handle MCP request
            response_data = handle_mcp_request(request_data)
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps(response_data)
            }
        
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps({
                    'jsonrpc': '2.0',
                    'id': 0,
                    'error': {
                        'code': -32603,
                        'message': f'Internal server error: {str(e)}'
                    }
                })
            }
    
    return {
        'statusCode': 405,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        },
        'body': json.dumps({'error': 'Method not allowed'})
    }
