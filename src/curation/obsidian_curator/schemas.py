"""
Pydantic schemas for LLM output validation.
Ensures structured outputs conform to expected formats.
"""
from typing import List, Dict, Optional
from pydantic import BaseModel, Field, field_validator

class UsefulnessResponse(BaseModel):
    """Schema for content usefulness assessment."""
    usefulness: float = Field(..., ge=0.0, le=1.0, description="Usefulness score from 0 to 1")
    reasoning: str = Field(..., min_length=10, description="Explanation for the score")
    
    @field_validator('usefulness')
    @classmethod
    def clamp_usefulness(cls, v: float) -> float:
        """Ensure usefulness is clamped between 0 and 1."""
        return max(0.0, min(1.0, v))

class EntityExtraction(BaseModel):
    """Schema for extracted entities."""
    organizations: List[str] = Field(default_factory=list, max_length=6)
    projects: List[str] = Field(default_factory=list, max_length=6)
    technologies: List[str] = Field(default_factory=list, max_length=6)
    locations: List[str] = Field(default_factory=list, max_length=6)

class ClassificationResponse(BaseModel):
    """Schema for content classification."""
    categories: List[str] = Field(..., min_length=1, max_length=3, description="1-3 infrastructure taxonomy categories")
    tags: List[str] = Field(..., min_length=5, max_length=10, description="5-10 professional tags")
    entities: EntityExtraction = Field(default_factory=EntityExtraction)
    publication_readiness: float = Field(..., ge=0.0, le=1.0, description="Publication readiness score from 0 to 1")
    
    @field_validator('publication_readiness')
    @classmethod
    def clamp_readiness(cls, v: float) -> float:
        """Ensure publication_readiness is clamped between 0 and 1."""
        return max(0.0, min(1.0, v))
    
    @field_validator('categories')
    @classmethod
    def validate_category_count(cls, v: List[str]) -> List[str]:
        """Ensure 1-3 categories are provided."""
        if len(v) > 3:
            return v[:3]
        return v
    
    @field_validator('tags')
    @classmethod
    def validate_tag_count(cls, v: List[str]) -> List[str]:
        """Ensure 5-10 tags are provided."""
        if len(v) < 5:
            # Pad with generic tags if needed
            while len(v) < 5:
                v.append("general")
        if len(v) > 10:
            return v[:10]
        return v

