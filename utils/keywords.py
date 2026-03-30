"""
키워드 설정 파일 읽기 유틸리티
"""
import yaml
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def load_keywords(path: str = "config/keywords.yaml") -> dict:
    """
    YAML 파일에서 키워드 설정을 읽어옴

    Args:
        path: keywords.yaml 파일 경로

    Returns:
        {
            "keywords": list,
            "location": str,
            "combination": str,
            "exclude": list,
            "experience": dict
        }
    """
    default_config = {
        "keywords": [],
        "location": "한국",
        "combination": "OR",
        "exclude": [],
        "experience": {"min": 0, "max": 10}
    }

    try:
        config_path = Path(path)
        if not config_path.exists():
            logger.warning(f"설정 파일을 찾을 수 없습니다: {path}")
            return default_config

        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        if config is None:
            logger.warning("설정 파일이 비어있습니다")
            return default_config

        # 필수 필드 검증 및 기본값 적용
        result = {
            "keywords": config.get("keywords", []),
            "location": config.get("location", "한국"),
            "combination": config.get("combination", "OR").upper(),
            "exclude": config.get("exclude", []),
            "experience": config.get("experience", {"min": 0, "max": 10})
        }

        # 키워드가 없으면 경고
        if not result["keywords"]:
            logger.warning("검색할 키워드가 설정되지 않았습니다")

        # combination 값 검증
        if result["combination"] not in ("AND", "OR"):
            logger.warning(f"잘못된 combination 값: {result['combination']}, 'OR'로 설정됨")
            result["combination"] = "OR"

        logger.info(f"키워드 설정 로드 완료: {len(result['keywords'])}개 키워드")
        return result

    except yaml.YAMLError as e:
        logger.error(f"YAML 파싱 오류: {e}")
        return default_config
    except Exception as e:
        logger.error(f"설정 파일 읽기 오류: {e}")
        return default_config
