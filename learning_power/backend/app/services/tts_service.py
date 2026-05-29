"""
语音合成服务 (Text-to-Speech Service)
支持多种TTS引擎：SiliconFlow TTS（推荐）、Edge TTS（备用）
"""
import edge_tts
import asyncio
import os
import hashlib
from pathlib import Path
from typing import Optional, Dict, List
import logging
import requests
from flask import current_app

logger = logging.getLogger(__name__)


class TTSService:
    """语音合成服务类"""

    # SiliconFlow TTS 音色配置（更自然流畅）
    SILICONFLOW_VOICES = {
        'xiaoxiao': {
            'name': 'zh-CN-XiaoxiaoNeural',
            'gender': 'Female',
            'description': '晓晓 - 温柔女声，自然流畅，适合讲故事'
        },
        'xiaochen': {
            'name': 'zh-CN-XiaochenNeural',
            'gender': 'Female',
            'description': '晓辰 - 甜美女声，活泼可爱，适合对话'
        },
        'xiaomo': {
            'name': 'zh-CN-XiaomoNeural',
            'gender': 'Female',
            'description': '晓墨 - 知性女声，专业稳重，适合教学'
        },
        'yunxi': {
            'name': 'zh-CN-YunxiNeural',
            'gender': 'Male',
            'description': '云希 - 成熟男声，沉稳大气，适合播报'
        },
        'yunyang': {
            'name': 'zh-CN-YunyangNeural',
            'gender': 'Male',
            'description': '云扬 - 专业男声，清晰有力，适合新闻'
        }
    }

    # Edge TTS 音色配置（备用）
    EDGE_VOICES = {
        'xiaoxiao': {
            'name': 'zh-CN-XiaoxiaoNeural',
            'gender': 'Female',
            'description': '晓晓 - 温柔女声，适合讲故事'
        },
        'yunxi': {
            'name': 'zh-CN-YunxiNeural',
            'gender': 'Male',
            'description': '云希 - 成熟男声，适合播报'
        },
        'xiaoyi': {
            'name': 'zh-CN-XiaoyiNeural',
            'gender': 'Female',
            'description': '晓伊 - 活泼女声，适合对话'
        },
        'yunjian': {
            'name': 'zh-CN-YunjianNeural',
            'gender': 'Male',
            'description': '云健 - 年轻男声，适合教学'
        }
    }

    def __init__(self, cache_dir: str = 'cache/tts', engine: str = 'siliconflow'):
        """
        初始化 TTS 服务

        Args:
            cache_dir: 音频缓存目录
            engine: TTS引擎 ('siliconflow' 或 'edge')
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.engine = engine
        logger.info(f"TTS 服务初始化完成，引擎: {engine}, 缓存目录: {self.cache_dir}")
    
    def _get_cache_path(self, text: str, voice: str, rate: str, pitch: str) -> Path:
        """
        生成缓存文件路径
        
        Args:
            text: 文本内容
            voice: 音色名称
            rate: 语速
            pitch: 音调
            
        Returns:
            缓存文件路径
        """
        # 使用文本和参数的哈希值作为文件名
        cache_key = f"{text}_{voice}_{rate}_{pitch}"
        hash_value = hashlib.md5(cache_key.encode()).hexdigest()
        return self.cache_dir / f"{hash_value}.mp3"
    
    async def synthesize_async(
        self,
        text: str,
        voice: str = 'xiaoxiao',
        rate: str = '+0%',
        pitch: str = '+0Hz',
        volume: str = '+0%'
    ) -> bytes:
        """
        异步合成语音
        
        Args:
            text: 要合成的文本
            voice: 音色 ID (xiaoxiao, yunxi, xiaoyi, yunjian, xiaoxuan, yunyang)
            rate: 语速调整 (-50% 到 +100%)
            pitch: 音调调整 (-50Hz 到 +50Hz)
            volume: 音量调整 (-50% 到 +50%)
            
        Returns:
            音频数据 (MP3 格式)
        """
        try:
            # 检查缓存
            cache_path = self._get_cache_path(text, voice, rate, pitch)
            if cache_path.exists():
                logger.info(f"使用缓存音频: {cache_path}")
                with open(cache_path, 'rb') as f:
                    return f.read()

            # 获取音色名称（使用 Edge TTS 音色配置）
            voice_name = self.EDGE_VOICES.get(voice, self.EDGE_VOICES['xiaoxiao'])['name']

            logger.info(f"开始合成语音: text='{text[:50]}...', voice={voice_name}")
            
            # 创建 TTS 通信对象
            communicate = edge_tts.Communicate(
                text=text,
                voice=voice_name,
                rate=rate,
                pitch=pitch,
                volume=volume
            )
            
            # 合成音频
            audio_data = b''
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            
            # 保存到缓存
            with open(cache_path, 'wb') as f:
                f.write(audio_data)
            
            logger.info(f"语音合成成功，大小: {len(audio_data)} bytes")
            return audio_data
            
        except Exception as e:
            logger.error(f"语音合成失败: {str(e)}")
            raise
    
    def synthesize_with_siliconflow(
        self,
        text: str,
        voice: str = 'xiaoxiao',
        rate: str = '+0%',
        pitch: str = '+0Hz',
        volume: str = '+0%'
    ) -> bytes:
        """
        使用 SiliconFlow TTS 合成语音（更流畅自然）

        Args:
            text: 要合成的文本
            voice: 音色 ID
            rate: 语速调整
            pitch: 音调调整
            volume: 音量调整

        Returns:
            音频数据 (MP3 格式)
        """
        try:
            # 检查缓存
            cache_path = self._get_cache_path(text, voice, rate, pitch)
            if cache_path.exists():
                logger.info(f"使用缓存音频: {cache_path}")
                with open(cache_path, 'rb') as f:
                    return f.read()

            # 获取音色名称
            voice_name = self.SILICONFLOW_VOICES.get(voice, self.SILICONFLOW_VOICES['xiaoxiao'])['name']

            # 从配置获取API密钥
            api_key = os.getenv('SILICONFLOW_API_KEY')
            if not api_key:
                raise Exception("SILICONFLOW_API_KEY 未配置")

            base_url = os.getenv('SILICONFLOW_BASE_URL', 'https://api.siliconflow.cn/v1')

            logger.info(f"使用 SiliconFlow TTS 合成: text='{text[:50]}...', voice={voice_name}")

            # 调用 SiliconFlow TTS API
            # 注意：这里使用的是假设的API端点，实际需要根据SiliconFlow文档调整
            url = f"{base_url}/audio/speech"

            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }

            # 转换参数格式
            speed = 1.0
            if rate:
                rate_value = int(rate.replace('%', '').replace('+', ''))
                speed = 1.0 + (rate_value / 100.0)

            payload = {
                'model': 'tts-1',  # 或 'tts-1-hd' 获得更高质量
                'input': text,
                'voice': voice_name.lower().replace('neural', '').replace('zh-cn-', ''),
                'speed': speed,
                'response_format': 'mp3'
            }

            response = requests.post(url, headers=headers, json=payload, timeout=30)

            if response.status_code != 200:
                raise Exception(f"SiliconFlow TTS API 错误: {response.status_code} - {response.text}")

            audio_data = response.content

            # 保存到缓存
            with open(cache_path, 'wb') as f:
                f.write(audio_data)

            logger.info(f"SiliconFlow TTS 合成成功，大小: {len(audio_data)} bytes")
            return audio_data

        except Exception as e:
            logger.error(f"SiliconFlow TTS 合成失败: {str(e)}")
            raise

    def synthesize(
        self,
        text: str,
        voice: str = 'xiaoxiao',
        rate: str = '+0%',
        pitch: str = '+0Hz',
        volume: str = '+0%'
    ) -> bytes:
        """
        同步合成语音（根据配置选择引擎）

        Args:
            text: 要合成的文本
            voice: 音色 ID
            rate: 语速调整
            pitch: 音调调整
            volume: 音量调整

        Returns:
            音频数据 (MP3 格式)
        """
        # 优先使用 SiliconFlow TTS
        if self.engine == 'siliconflow':
            try:
                return self.synthesize_with_siliconflow(text, voice, rate, pitch, volume)
            except Exception as e:
                logger.warning(f"SiliconFlow TTS 失败，回退到 Edge TTS: {str(e)}")
                self.engine = 'edge'  # 临时切换到备用引擎

        # 使用 Edge TTS（备用）
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(
            self.synthesize_async(text, voice, rate, pitch, volume)
        )
    
    @classmethod
    def get_available_voices(cls, engine: str = 'siliconflow') -> List[Dict]:
        """
        获取可用的音色列表

        Args:
            engine: TTS引擎 ('siliconflow' 或 'edge')

        Returns:
            音色列表
        """
        voices_dict = cls.SILICONFLOW_VOICES if engine == 'siliconflow' else cls.EDGE_VOICES

        return [
            {
                'id': voice_id,
                'name': voice_info['name'],
                'gender': voice_info['gender'],
                'description': voice_info['description']
            }
            for voice_id, voice_info in voices_dict.items()
        ]
    
    def clear_cache(self) -> int:
        """
        清空缓存
        
        Returns:
            删除的文件数量
        """
        count = 0
        for file in self.cache_dir.glob('*.mp3'):
            file.unlink()
            count += 1
        logger.info(f"清空缓存完成，删除 {count} 个文件")
        return count


# 全局 TTS 服务实例
_tts_service = None


def get_tts_service() -> TTSService:
    """获取 TTS 服务单例"""
    global _tts_service
    if _tts_service is None:
        # 默认使用 Edge TTS（免费、稳定）
        engine = os.getenv('TTS_ENGINE', 'edge')
        _tts_service = TTSService(engine=engine)
    return _tts_service

