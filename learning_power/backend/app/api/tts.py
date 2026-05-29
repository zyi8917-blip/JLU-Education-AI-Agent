"""
语音合成 API
提供文本转语音服务
"""
from flask import Blueprint, request, jsonify, send_file
from io import BytesIO
import logging
from app.services.tts_service import get_tts_service

logger = logging.getLogger(__name__)

tts_bp = Blueprint('tts', __name__)


@tts_bp.route('/synthesize', methods=['POST'])
def synthesize():
    """
    合成语音
    
    请求体:
    {
        "text": "要合成的文本",
        "voice": "xiaoxiao",  // 可选，默认 xiaoxiao
        "rate": "+0%",        // 可选，语速 -50% 到 +100%
        "pitch": "+0Hz",      // 可选，音调 -50Hz 到 +50Hz
        "volume": "+0%"       // 可选，音量 -50% 到 +50%
    }
    
    返回:
        音频文件 (audio/mpeg)
    """
    try:
        data = request.get_json()
        
        # 验证必填参数
        if not data or 'text' not in data:
            return jsonify({
                'error': '缺少必填参数 text'
            }), 400
        
        text = data['text']
        
        # 验证文本长度
        if len(text) > 5000:
            return jsonify({
                'error': '文本长度不能超过 5000 字符'
            }), 400
        
        # 获取可选参数
        voice = data.get('voice', 'xiaoxiao')
        rate = data.get('rate', '+0%')
        pitch = data.get('pitch', '+0Hz')
        volume = data.get('volume', '+0%')
        
        logger.info(f"收到语音合成请求: text='{text[:50]}...', voice={voice}")

        # 合成语音
        tts_service = get_tts_service()

        try:
            audio_data = tts_service.synthesize(
                text=text,
                voice=voice,
                rate=rate,
                pitch=pitch,
                volume=volume
            )

            # 返回音频文件
            return send_file(
                BytesIO(audio_data),
                mimetype='audio/mpeg',
                as_attachment=False,
                download_name='speech.mp3'
            )
        except Exception as tts_error:
            # Edge TTS 服务失败，返回 503 让前端回退到浏览器 TTS
            logger.warning(f"Edge TTS 服务失败: {str(tts_error)}, 前端将回退到浏览器 TTS")
            return jsonify({
                'error': 'Edge TTS 服务暂时不可用',
                'fallback': 'browser_tts',
                'message': str(tts_error)
            }), 503  # Service Unavailable

    except Exception as e:
        logger.error(f"语音合成请求处理失败: {str(e)}", exc_info=True)
        return jsonify({
            'error': f'语音合成请求处理失败: {str(e)}'
        }), 500


@tts_bp.route('/voices', methods=['GET'])
def get_voices():
    """
    获取可用的音色列表
    
    返回:
    {
        "voices": [
            {
                "id": "xiaoxiao",
                "name": "zh-CN-XiaoxiaoNeural",
                "gender": "Female",
                "description": "晓晓 - 温柔女声，适合讲故事"
            },
            ...
        ]
    }
    """
    try:
        tts_service = get_tts_service()
        voices = tts_service.get_available_voices()
        
        return jsonify({
            'voices': voices
        })
        
    except Exception as e:
        logger.error(f"获取音色列表失败: {str(e)}", exc_info=True)
        return jsonify({
            'error': f'获取音色列表失败: {str(e)}'
        }), 500


@tts_bp.route('/cache/clear', methods=['POST'])
def clear_cache():
    """
    清空语音缓存
    
    返回:
    {
        "message": "缓存清空成功",
        "count": 10
    }
    """
    try:
        tts_service = get_tts_service()
        count = tts_service.clear_cache()
        
        return jsonify({
            'message': '缓存清空成功',
            'count': count
        })
        
    except Exception as e:
        logger.error(f"清空缓存失败: {str(e)}", exc_info=True)
        return jsonify({
            'error': f'清空缓存失败: {str(e)}'
        }), 500

