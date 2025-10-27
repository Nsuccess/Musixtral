# MusicToolkit MCP Server

A FastMCP server that provides music processing tools for converting audio to music scores and generating music from humming.

## Features

### 🎼 WAV to Music Score
- Converts WAV audio files to MusicXML scores using pitch detection
- Renders music scores as SVG images via Verovio API
- Uses basic-pitch for audio-to-MIDI conversion and music21 for MusicXML generation

### 🎵 Music Generation from Humming
- Generates full music tracks from humming audio files
- Uses AI music generation API (MusicGen) with style prompts
- Optionally generates music scores from the generated audio

## MCP Tools

1. **`wav_to_music_score`** - Convert WAV files to MusicXML scores with optional SVG rendering
2. **`generate_music_from_humming`** - Generate music from humming with optional score generation

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment (optional):
```bash
export PORT=8001  # Default port for the server
```

## Usage

### Running the Server
```bash
uv run python music_toolkit_server.py
```

The server runs in STDIO mode for MCP protocol communication.

### MCP Client Configuration
Configure your MCP client to use this server as a local executable:
- **Command**: `uv run python music_toolkit_server.py`
- **Working Directory**: `/path/to/MusicToolkit/`
- **Protocol**: STDIO/JSON-RPC 2.0

### Usage with Le Chat or other MCP clients

**Local Usage:**
1. Add the server to your MCP client configuration
2. Use command: `uv run python music_toolkit_server.py`

### Deployment

### Vercel Deployment
The MCP server is deployed on Vercel and accessible at:
- **Production URL**: https://musictoolkit.vercel.app
- **MCP Endpoint**: https://musictoolkit.vercel.app/mcp
- **Direct API**: https://musictoolkit.vercel.app/api/mcp

The server provides two main tools:
- `wav_to_music_score` - Convert WAV files to music scores
- `generate_music_from_humming` - Generate music from humming audio

## API Endpoints

The server uses external APIs for enhanced functionality:
- **Verovio API**: `https://ykzou1214--verovio-api-fastapi-app.modal.run` (Music score rendering)
- **MusicGen API**: `https://ykzou1214--musicgen-melody-api-inference-api.modal.run` (AI music generation)

## Dependencies

- `fastmcp` - MCP server framework
- `basic-pitch` - Audio-to-MIDI conversion
- `music21` - Music analysis and MusicXML generation
- `requests` - HTTP client for API calls
- `pydantic` - Data validation

## Output Directory

Generated files are saved to the `output/` directory:
- MusicXML files: `generated_YYYYMMDD_HHMMSS.musicxml`
- Generated music: `generated_YYYYMMDD_HHMMSS.wav`

## Example Usage

### Converting WAV to Music Score
```python
# Via MCP client
result = client.call_tool("wav_to_music_score", {
    "wav_file_path": "/path/to/audio.wav",
    "render_svg": True
})
```

### Generating Music from Humming
```python
# Via MCP client
result = client.call_tool("generate_music_from_humming", {
    "humming_file_path": "/path/to/humming.wav",
    "style_prompt": "upbeat pop song with guitar and drums",
    "generate_score": True
})
```

## Error Handling

The server includes comprehensive error handling for:
- Missing input files
- API connection failures
- Library import errors
- File processing errors

## Troubleshooting

1. **Missing Libraries**: Install `basic-pitch` and `music21` if you get import errors
2. **API Errors**: Check network connectivity to external APIs
3. **File Permissions**: Ensure the server has read/write access to input/output directories
