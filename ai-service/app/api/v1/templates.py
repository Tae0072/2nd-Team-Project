from fastapi import APIRouter
from typing import Optional

router = APIRouter()


@router.get("")
async def list_prompt_templates(stage: Optional[str] = None):
    """프롬프트 템플릿 목록 (큐티 A~D)"""
    # TODO: DB에서 조회
    return {"data": [], "message": "구현 예정 (W1 DB 초기화 후)"}