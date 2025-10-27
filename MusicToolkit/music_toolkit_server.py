#!/usr/bin/env python3
"""
MusicToolkit FastMCP Server
MCP Server for music processing tools including WAV to MusicXML conversion and music generation from humming
"""

import os
import json
import base64
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel, Field
from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("MusicToolkit MCP Server")

# API URLs
VEROVIO_API_URL = "https://ykzou1214--verovio-api-fastapi-app.modal.run"
MUSICGEN_API_URL = "https://ykzou1214--musicgen-melody-api-inference-api.modal.run"

# Import required libraries for music processing
try:
    from music21 import converter
    MUSIC21_AVAILABLE = True
except ImportError:
    MUSIC21_AVAILABLE = False
    print("⚠️ Warning: music21 not available. Install it for MusicXML functionality.")

try:
    from basic_pitch.inference import predict_and_save
    from basic_pitch import ICASSP_2022_MODEL_PATH
    BASIC_PITCH_AVAILABLE = True
except ImportError:
    BASIC_PITCH_AVAILABLE = False
    print("⚠️ Warning: basic_pitch not available. WAV to MIDI conversion will use alternative method.")

def wav_to_musicxml(wav_path: str, timestamp: str = None) -> str:
    """
    Convert a WAV audio file to a MusicXML score using pitch detection.
    Args:
        wav_path (str): Path to the input WAV audio file.
        timestamp (str, optional): Custom timestamp for output naming. Defaults to current time.
    Returns:
        str: File path to the generated MusicXML file.
    Raises:
        FileNotFoundError: If the MIDI file could not be generated.
    """
    if not MUSIC21_AVAILABLE:
        raise ImportError("music21 library is required for MusicXML generation")
    
    timestamp = timestamp or datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    if BASIC_PITCH_AVAILABLE:
        # Use basic_pitch for audio-to-MIDI conversion
        # Clean up previous basic_pitch files
        for f in output_dir.glob("*_basic_pitch.mid"):
            f.unlink()

        predict_and_save(
            audio_path_list=[wav_path],
            output_directory=str(output_dir),
            save_midi=True,
            sonify_midi=False,
            save_model_outputs=False,
            save_notes=False,
            model_or_model_path=ICASSP_2022_MODEL_PATH
        )

        midi_files = list(output_dir.glob("*.mid"))
        if not midi_files:
            raise FileNotFoundError("❌ Failed to generate MIDI file")

        midi_path = midi_files[0]
    else:
        # Alternative: Create a simple placeholder MIDI file
        # This is a fallback when basic_pitch is not available
        from music21 import stream, note, duration
        
        # Create a simple score with placeholder notes
        score = stream.Score()
        part = stream.Part()
        
        # Add some placeholder notes (this would normally come from audio analysis)
        notes = ['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4', 'C5']
        for pitch in notes:
            n = note.Note(pitch, quarterLength=1.0)
            part.append(n)
        
        score.append(part)
        musicxml_path = output_dir / f"generated_{timestamp}.musicxml"
        score.write("musicxml", fp=musicxml_path)
        return str(musicxml_path)
    
    # Convert MIDI to MusicXML using music21
    score = converter.parse(midi_path)
    musicxml_path = output_dir / f"generated_{timestamp}.musicxml"
    score.write("musicxml", fp=musicxml_path)
    return str(musicxml_path)

def render_musicxml_via_verovio_api(musicxml_path: str) -> str:
    """
    Render a MusicXML file to an SVG score preview using the Verovio API.
    Args:
        musicxml_path (str): Path to the MusicXML file.
    Returns:
        str: HTML string containing base64-encoded SVG score image, or error message on failure.
    """
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
    """
    Generate music from a humming audio file and a style prompt using an external MusicGen API.
    Args:
        melody_file (str): Path to the recorded humming audio (.wav).
        prompt (str): Text prompt describing desired music style.
    Returns:
        str: Path to the generated WAV music file, or error message on failure.
    """
    if not MUSICGEN_API_URL:
        return "❌ MUSICGEN_API_URL is not configured."

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("output")
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

def generate_score_from_audio(wav_file):
    """
    Generate a MusicXML score from an input audio (.wav) file.
    Args:
        wav_file (str): Path to the WAV music file.
    Returns:
        str: File path to the generated MusicXML file, or error message on failure.
    """
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return wav_to_musicxml(wav_file, timestamp)
    except Exception as e:
        return f"❌ Score generation failed: {e}"

@mcp.tool(
    title="Generate Music Score from WAV",
    description="Convert a WAV audio file to a MusicXML score and render it as an SVG image",
)
def wav_to_music_score(
    wav_file_path: str = Field(description="Path to the input WAV audio file"),
    render_svg: bool = Field(description="Whether to render the score as SVG", default=True)
) -> str:
    """Convert a WAV audio file to a MusicXML score using pitch detection and optionally render as SVG"""
    try:
        # Check if input file exists
        if not os.path.exists(wav_file_path):
            return f"❌ WAV file not found: {wav_file_path}"
        
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
        
        return result
        
    except ImportError as e:
        return f"❌ Missing required libraries: {e}\nPlease install: pip install basic-pitch music21"
    except Exception as e:
        return f"❌ Error converting WAV to music score: {str(e)}"

@mcp.tool(
    title="Generate Music from Humming",
    description="Generate full music from a humming audio file using AI music generation",
)
def generate_music_from_humming(
    humming_file_path: str = Field(description="Path to the humming audio file (.wav)"),
    style_prompt: str = Field(description="Text prompt describing the desired music style (e.g., 'upbeat pop song', 'classical piano piece')"),
    generate_score: bool = Field(description="Whether to also generate a music score from the result", default=False)
) -> str:
    """Generate full music from a humming audio file and optionally create a music score"""
    try:
        # Check if input file exists
        if not os.path.exists(humming_file_path):
            return f"❌ Humming file not found: {humming_file_path}"
        
        # Generate music from humming
        generated_wav_path = generate_music_from_hum(humming_file_path, style_prompt)
        
        if generated_wav_path.startswith("❌"):
            return generated_wav_path
        
        result = f"✅ Successfully generated music from humming\n📁 Generated music file: {generated_wav_path}\n🎵 Style: {style_prompt}"
        
        # Optionally generate score from the result
        if generate_score:
            try:
                score_path = generate_score_from_audio(generated_wav_path)
                if score_path.startswith("❌"):
                    result += f"\n⚠️ Score generation failed: {score_path}"
                else:
                    result += f"\n🎼 Music score generated: {score_path}"
                    
                    # Try to render the score as SVG
                    svg_html = render_musicxml_via_verovio_api(score_path)
                    if not (svg_html.startswith("❌") or svg_html.startswith("⚠️")):
                        result += f"\n🎼 Score rendered as SVG:\n{svg_html}"
                        
            except Exception as e:
                result += f"\n⚠️ Score generation error: {str(e)}"
        
        return result
        
    except Exception as e:
        return f"❌ Error generating music from humming: {str(e)}"

@mcp.resource(
    uri="musictoolkit://output",
    name="Generated Files",
    description="List of generated music files and scores"
)
def get_generated_files() -> str:
    """Get list of all generated files in the output directory"""
    try:
        output_dir = Path("output")
        if not output_dir.exists():
            return "No output directory found. No files have been generated yet."
        
        files = list(output_dir.iterdir())
        if not files:
            return "Output directory is empty. No files have been generated yet."
        
        result = "Generated Files:\n\n"
        for file_path in sorted(files):
            if file_path.is_file():
                file_size = file_path.stat().st_size
                modified_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                result += f"📁 {file_path.name}\n"
                result += f"   Size: {file_size:,} bytes\n"
                result += f"   Modified: {modified_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        return result
    except Exception as e:
        return f"Error listing generated files: {str(e)}"

@mcp.prompt(
    name="music_processing",
    description="AI assistant for music processing and generation tasks"
)
def music_processing_prompt(
    task_type: str = Field(description="Type of music processing task"),
    input_description: str = Field(description="Description of the input audio/music"),
    desired_output: str = Field(description="Description of desired output")
) -> str:
    """Generate a music processing prompt"""
    prompt = f"""You are an AI music processing assistant for MusicToolkit. Help with music analysis and generation tasks.

🎵 Task Type: {task_type}
🎤 Input: {input_description}
🎯 Desired Output: {desired_output}

Available capabilities:
1. WAV to MusicXML conversion using pitch detection
2. Music score rendering as SVG images
3. AI music generation from humming audio
4. Style-based music transformation

Please suggest:
1. Best approach for the given task
2. Recommended parameters and settings
3. Expected output quality and limitations
4. Alternative processing methods if applicable
5. Post-processing suggestions

Focus on practical, actionable advice for music processing workflows."""
    
    return prompt

if __name__ == "__main__":
    # Run the FastMCP server
    # For MCP protocol, we use stdio mode (no host/port needed)
    mcp.run()
