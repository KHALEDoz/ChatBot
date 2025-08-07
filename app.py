from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import os
from dotenv import load_dotenv
import json
from datetime import datetime
from audio_processor import AudioProcessor
from llm_processor import LLMProcessor

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize processors
audio_processor = AudioProcessor()
llm_processor = LLMProcessor()

# In-memory storage for conversations (in production, use a database)
conversations = {}

@app.route('/')
def index():
    """Serve the main chat interface"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        conversation_id = data.get('conversation_id', 'default')
        use_cohere = data.get('use_cohere', True)
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get or create conversation
        if conversation_id not in conversations:
            conversations[conversation_id] = []
        
        # Add user message to conversation
        user_message = {
            'id': len(conversations[conversation_id]) + 1,
            'sender': 'user',
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        conversations[conversation_id].append(user_message)
        
        # Get bot response using LLM processor
        bot_response = llm_processor.generate_response(message, conversation_id, use_cohere)
        
        # Add bot response to conversation
        bot_message = {
            'id': len(conversations[conversation_id]) + 1,
            'sender': 'bot',
            'message': bot_response,
            'timestamp': datetime.now().isoformat()
        }
        conversations[conversation_id].append(bot_message)
        
        return jsonify({
            'response': bot_response,
            'conversation_id': conversation_id,
            'message_id': bot_message['id']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversations/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """Get conversation history"""
    try:
        conversation = conversations.get(conversation_id, [])
        return jsonify({
            'conversation_id': conversation_id,
            'messages': conversation
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversations', methods=['GET'])
def get_all_conversations():
    """Get all conversations"""
    try:
        return jsonify({
            'conversations': list(conversations.keys()),
            'count': len(conversations)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversations/<conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    """Delete a conversation"""
    try:
        if conversation_id in conversations:
            del conversations[conversation_id]
            return jsonify({'message': 'Conversation deleted successfully'})
        else:
            return jsonify({'error': 'Conversation not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/audio/speech-to-text', methods=['POST'])
def speech_to_text():
    """Convert speech to text"""
    try:
        data = request.get_json()
        audio_data = data.get('audio_data')
        
        if not audio_data:
            return jsonify({'error': 'Audio data is required'}), 400
        
        # Convert speech to text
        result = audio_processor.speech_to_text(audio_data=audio_data)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/audio/text-to-speech', methods=['POST'])
def text_to_speech():
    """Convert text to speech"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        # Convert text to speech
        result = audio_processor.text_to_speech(text, save_to_file=True)
        
        if result['success']:
            # Convert audio file to base64 for web transmission
            base64_audio = audio_processor.get_audio_base64(result['audio_file'])
            
            return jsonify({
                'success': True,
                'audio_data': base64_audio,
                'audio_file': result['audio_file']
            })
        else:
            return jsonify(result), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/audio/chat', methods=['POST'])
def audio_chat():
    """Complete audio chat pipeline: speech-to-text -> LLM -> text-to-speech"""
    try:
        data = request.get_json()
        audio_data = data.get('audio_data')
        conversation_id = data.get('conversation_id', 'default')
        use_cohere = data.get('use_cohere', True)
        
        if not audio_data:
            return jsonify({'error': 'Audio data is required'}), 400
        
        # Step 1: Convert speech to text
        stt_result = audio_processor.speech_to_text(audio_data=audio_data)
        if not stt_result['success']:
            return jsonify(stt_result), 400
        
        user_text = stt_result['text']
        
        # Step 2: Generate response using LLM
        bot_response = llm_processor.generate_response(user_text, conversation_id, use_cohere)
        
        # Step 3: Convert response to speech
        tts_result = audio_processor.text_to_speech(bot_response, save_to_file=True)
        if not tts_result['success']:
            return jsonify(tts_result), 500
        
        # Convert audio file to base64
        base64_audio = audio_processor.get_audio_base64(tts_result['audio_file'])
        
        # Update conversation history
        if conversation_id not in conversations:
            conversations[conversation_id] = []
        
        user_message = {
            'id': len(conversations[conversation_id]) + 1,
            'sender': 'user',
            'message': user_text,
            'timestamp': datetime.now().isoformat()
        }
        conversations[conversation_id].append(user_message)
        
        bot_message = {
            'id': len(conversations[conversation_id]) + 1,
            'sender': 'bot',
            'message': bot_response,
            'timestamp': datetime.now().isoformat()
        }
        conversations[conversation_id].append(bot_message)
        
        return jsonify({
            'success': True,
            'user_text': user_text,
            'bot_response': bot_response,
            'audio_data': base64_audio,
            'conversation_id': conversation_id,
            'message_id': bot_message['id']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'bot_name': 'AI Assistant',
        'features': {
            'text_chat': True,
            'audio_chat': True,
            'speech_to_text': True,
            'text_to_speech': True,
            'llm_integration': True
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port) 