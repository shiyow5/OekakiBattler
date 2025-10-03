"""
AI analyzer service for character stat generation
"""

import os
import json
import logging
from PIL import Image
from typing import Optional, Dict, Any
import numpy as np
from src.models import CharacterStats
from config.settings import Settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import Google AI, but handle gracefully if not available
try:
    from google import genai
    GOOGLE_AI_AVAILABLE = True
except ImportError:
    GOOGLE_AI_AVAILABLE = False
    logger.warning("Google Generative AI not available. AI analysis will use fallback mode.")

class AIAnalyzer:
    """AI service for analyzing character images and generating stats"""
    
    def __init__(self):
        self.model_name = Settings.MODEL_NAME
        self.api_key = Settings.GOOGLE_API_KEY
        self.google_ai_available = GOOGLE_AI_AVAILABLE
        
        if GOOGLE_AI_AVAILABLE and self.api_key:
            try:
                self.client = genai.Client()
                logger.info("Google AI client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Google AI client: {e}")
                self.google_ai_available = False
        else:
            self.client = None
            if not GOOGLE_AI_AVAILABLE:
                logger.warning("Google AI library not installed")
            if not self.api_key:
                logger.warning("Google API key not found. Please set GOOGLE_API_KEY in .env file")
    
    def analyze_character(self, image_path: str, fallback_stats: bool = True) -> Optional[CharacterStats]:
        """Analyze character image and generate stats with multiple approaches"""
        try:
            # Load and validate image
            image = Image.open(image_path)
            logger.info(f"Analyzing character image: {image_path}")
            
            # Check if Google AI is available
            if self.google_ai_available and self.client:
                # Try primary analysis method
                stats = self._analyze_with_detailed_prompt(image)
                if stats:
                    logger.info("Character analysis successful with detailed prompt")
                    return stats
                
                # Try simplified analysis if detailed fails
                logger.warning("Detailed analysis failed, trying simplified approach")
                stats = self._analyze_with_simple_prompt(image)
                if stats:
                    logger.info("Character analysis successful with simple prompt")
                    return stats
            else:
                logger.info("Google AI not available, using fallback stats generation")
            
            # Generate fallback stats based on basic image analysis
            if fallback_stats:
                logger.info("Generating fallback stats")
                return self._generate_fallback_stats(image_path)
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing character: {e}")
            if fallback_stats:
                return self._generate_fallback_stats(image_path)
            return None
    
    def _analyze_with_detailed_prompt(self, image: Image.Image) -> Optional[CharacterStats]:
        """Analyze with detailed prompt for comprehensive stat generation"""
        try:
            prompt = self._get_detailed_analysis_prompt()
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt, image],
                config={
                    "response_mime_type": "application/json",
                    "response_schema": list[CharacterStats],
                },
            )
            
            # Parse response
            result_data = json.loads(response.text)
            if isinstance(result_data, list) and len(result_data) > 0:
                stats_data = result_data[0]
                # Validate and adjust stats
                validated_stats = self._validate_and_adjust_stats(stats_data)
                return CharacterStats(**validated_stats)
            
            return None
            
        except Exception as e:
            logger.warning(f"Detailed analysis failed: {e}")
            return None
    
    def _analyze_with_simple_prompt(self, image: Image.Image) -> Optional[CharacterStats]:
        """Analyze with simple prompt as fallback"""
        try:
            prompt = self._get_simple_analysis_prompt()
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt, image],
                config={
                    "response_mime_type": "application/json",
                    "response_schema": list[CharacterStats],
                },
            )
            
            # Parse response
            result_data = json.loads(response.text)
            if isinstance(result_data, list) and len(result_data) > 0:
                stats_data = result_data[0]
                validated_stats = self._validate_and_adjust_stats(stats_data)
                return CharacterStats(**validated_stats)
            
            return None
            
        except Exception as e:
            logger.warning(f"Simple analysis failed: {e}")
            return None
    
    def _get_detailed_analysis_prompt(self) -> str:
        """Get the comprehensive prompt for detailed character analysis"""
        return """
あなたは世界的に有名なゲームデザイナーとバランス調整の専門家です。
手描きキャラクターの絵を詳細に分析し、視覚的特徴からゲーム内での能力値を科学的に決定してください。

## キャラクター名の生成:
- 見た目の特徴を反映した日本語の名前を付けてください
- 10文字以内で覚えやすい名前にしてください
- 例: 「炎の戦士」「氷の魔法使い」「疾風の剣士」「鋼鉄の騎士」など

## 詳細分析基準:

### 1. 体力 (HP: 10-200)
- 体格の大きさ: 大きい→高HP、小さい→低HP
- 体の厚み: 厚い・筋肉質→高HP、細い→低HP
- 安定感: どっしりした→高HP、華奢な→低HP
- 防御的要素: 鎧・厚い服→HP+10-30

### 2. 攻撃力 (Attack: 10-150)
- 武器: 剣・斧・槍→+30-50、素手→基本値
- 筋肉: 明らかに筋肉質→+20-35
- 爪・牙: 鋭い爪や牙→+15-25
- 攻撃的ポーズ: 攻撃姿勢→+10-20
- 顔の表情: 凶暴・怒り→+5-15

### 3. 防御力 (Defense: 10-100)
- 鎧・防具: 重装鎧→+30-40、軽装→+10-20
- 盾: 大盾→+20-30、小盾→+10-15
- 体の硬さ: 岩石風→+20-30、金属風→+25-35
- 守備姿勢: 守備的ポーズ→+5-15

### 4. 素早さ (Speed: 10-100)
- 体型: スリム→高Speed、重い→低Speed
- 手足の長さ: 長い手足→+15-25
- 動的ポーズ: 走る・跳ぶポーズ→+15-25
- 軽装備: 軽い装備→+10-20
- 翼や風の要素: +20-30

### 5. 魔法力 (Magic: 10-100)
- 杖・魔法道具: +30-50
- 魔法陣・ルーン: +20-40
- 神秘的な装飾: +15-25
- オーラ・光の表現: +10-30
- 魔法的な色彩: 紫・青・金→+5-15

### 6. 運 (Luck: 0-100)
- 幸運のシンボル: クローバー・星→+30-50
- 明るい表情: 笑顔・楽しそう→+20-30
- キラキラした装飾: +15-25
- 光や輝きの表現: +10-20
- 可愛らしさ・愛嬌: +10-20

## 重要な制約:
**全ステータスの合計値は必ず350以下にしてください**
合計が350を超える場合は、各ステータスを比例的に減らして調整してください。

## 追加考慮事項:
- 絵の上手さは能力に影響しません
- バランス: 総合値が極端に高い/低い場合は調整
- 個性: 特徴的な要素は強化
- 説明文: そのキャラの最も印象的な特徴を30文字以内で

## 出力形式:
キャラクター名、各ステータスの数値（合計350以下）、分析理由を含んだ簡潔な説明文を返してください。
        """
    
    def _get_simple_analysis_prompt(self) -> str:
        """Get simplified prompt for basic analysis"""
        return """
手描きキャラクターを見て、ゲーム用のステータスを決めてください。

名前:
- 見た目の特徴を反映した日本語の名前（10文字以内）
- 例: 「勇者」「魔法使い」「剣士」など

判定基準:
- HP (10-200): 体の大きさ・頑丈さ
- Attack (10-150): 武器・筋肉・攻撃的な見た目
- Defense (10-100): 鎧・盾・体の硬さ
- Speed (10-100): 体型・手足の長さ・軽やかさ
- Magic (10-100): 杖・魔法的な装飾・神秘性
- Luck (0-100): 幸運のシンボル・明るい表情・キラキラした装飾

**重要: 全ステータスの合計は必ず350以下にしてください**

説明は30文字以内でキャラの特徴を表現してください。
        """
    
    def _validate_and_adjust_stats(self, stats_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and adjust generated stats to ensure they're within acceptable ranges"""
        try:
            # Validate and ensure name exists
            if 'name' not in stats_data or not stats_data['name']:
                stats_data['name'] = "未知のキャラクター"
            else:
                # Trim name to 30 characters max
                stats_data['name'] = str(stats_data['name'])[:30]

            # Define valid ranges
            ranges = {
                'hp': (10, 200),
                'attack': (10, 150),
                'defense': (10, 100),
                'speed': (10, 100),
                'magic': (10, 100),
                'luck': (0, 100)
            }

            # Validate and clamp values
            for stat, (min_val, max_val) in ranges.items():
                if stat in stats_data:
                    value = stats_data[stat]
                    if not isinstance(value, (int, float)):
                        logger.warning(f"Invalid {stat} value type: {type(value)}, using middle value")
                        stats_data[stat] = (min_val + max_val) // 2
                    else:
                        stats_data[stat] = max(min_val, min(max_val, int(value)))
                else:
                    # Generate default value if missing
                    if stat == 'luck':
                        stats_data[stat] = 50  # Default luck
                    else:
                        stats_data[stat] = (min_val + max_val) // 2

            # Check total stats and adjust if needed
            total_stats = stats_data['hp'] + stats_data['attack'] + stats_data['defense'] + stats_data['speed'] + stats_data['magic'] + stats_data['luck']
            if total_stats > 350:
                logger.warning(f"Total stats ({total_stats}) exceeds 350, adjusting proportionally")
                scale_factor = 350 / total_stats
                for stat in ['hp', 'attack', 'defense', 'speed', 'magic', 'luck']:
                    stats_data[stat] = max(ranges[stat][0], int(stats_data[stat] * scale_factor))

            # Ensure description exists and is reasonable
            if 'description' not in stats_data or not stats_data['description']:
                stats_data['description'] = "個性的なキャラクター"
            elif len(stats_data['description']) > 50:
                stats_data['description'] = stats_data['description'][:47] + "..."
            
            # Balance check - prevent extreme total stats
            total_stats = sum(stats_data[stat] for stat in ['hp', 'attack', 'defense', 'speed', 'magic'])
            if total_stats > 500:  # Too high, scale down
                scale_factor = 500 / total_stats
                for stat in ['hp', 'attack', 'defense', 'speed', 'magic']:
                    min_val, max_val = ranges[stat]
                    scaled_value = int(stats_data[stat] * scale_factor)
                    stats_data[stat] = max(min_val, min(max_val, scaled_value))
            elif total_stats < 200:  # Too low, scale up
                scale_factor = 200 / total_stats
                for stat in ['hp', 'attack', 'defense', 'speed', 'magic']:
                    min_val, max_val = ranges[stat]
                    scaled_value = int(stats_data[stat] * scale_factor)
                    stats_data[stat] = max(min_val, min(max_val, scaled_value))
            
            return stats_data
            
        except Exception as e:
            logger.error(f"Error validating stats: {e}")
            return self._get_default_stats()
    
    def _generate_fallback_stats(self, image_path: str) -> CharacterStats:
        """Generate reasonable fallback stats when AI analysis fails"""
        try:
            # Simple image-based heuristics
            image = Image.open(image_path)
            width, height = image.size

            # Convert to numpy array for basic analysis
            img_array = np.array(image)

            # Basic heuristics based on image properties
            base_stats = {
                'name': "未知のキャラクター",
                'hp': 80,  # Default values within new ranges
                'attack': 60,
                'defense': 50,
                'speed': 55,
                'magic': 55,
                'luck': 50,
                'description': "未知のキャラクター"
            }

            # Adjust based on image size (larger images might indicate larger characters)
            if width * height > 500000:  # Large image
                base_stats['hp'] += 20
                base_stats['defense'] += 15
                base_stats['speed'] -= 10
            elif width * height < 100000:  # Small image
                base_stats['hp'] -= 15
                base_stats['speed'] += 15
                base_stats['magic'] += 10

            # Add some randomness to make characters unique
            import random
            for stat in ['hp', 'attack', 'defense', 'speed', 'magic', 'luck']:
                variation = random.randint(-15, 15)
                base_stats[stat] += variation

            # Validate the generated stats (includes total check)
            validated_stats = self._validate_and_adjust_stats(base_stats)
            return CharacterStats(**validated_stats)
            
        except Exception as e:
            logger.error(f"Error generating fallback stats: {e}")
            return CharacterStats(**self._get_default_stats())
    
    def _get_default_stats(self) -> Dict[str, Any]:
        """Get default balanced stats"""
        return {
            'name': "バランス戦士",
            'hp': 70,
            'attack': 60,
            'defense': 50,
            'speed': 55,
            'magic': 55,
            'luck': 50,
            'description': "バランス型キャラクター"
        }
    
    def analyze_batch(self, image_paths: list) -> Dict[str, Optional[CharacterStats]]:
        """Analyze multiple character images in batch"""
        results = {}
        for image_path in image_paths:
            try:
                results[image_path] = self.analyze_character(image_path)
            except Exception as e:
                logger.error(f"Batch analysis failed for {image_path}: {e}")
                results[image_path] = None
        return results
    
    def test_api_connection(self) -> bool:
        """Test if API connection is working"""
        if not self.google_ai_available:
            logger.warning("Google AI not available - cannot test connection")
            return False
            
        if not self.client:
            logger.warning("Google AI client not initialized")
            return False
            
        try:
            # Simple test request
            test_response = self.client.models.generate_content(
                model=self.model_name,
                contents=["Hello, can you respond with 'API connection successful'?"]
            )
            
            if test_response and test_response.text:
                logger.info("API connection test successful")
                return True
            else:
                logger.error("API connection test failed - no response")
                return False
                
        except Exception as e:
            logger.error(f"API connection test failed: {e}")
            return False