from pydantic import BaseModel, Field
from typing import Optional


class ServiceCatalogBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    slug: str = Field(..., min_length=1, max_length=80)
    category: str = Field(..., min_length=1, max_length=30)
    provider: str = Field(..., min_length=1, max_length=60)
    default_config: Optional[dict] = None
    is_active: bool = True


class ServiceCatalogCreate(ServiceCatalogBase):
    pass


class ServiceCatalogUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=120)
    slug: Optional[str] = Field(None, min_length=1, max_length=80)
    category: Optional[str] = Field(None, min_length=1, max_length=30)
    provider: Optional[str] = Field(None, min_length=1, max_length=60)
    default_config: Optional[dict] = None
    is_active: Optional[bool] = None


class ServiceCatalogBulkUpdate(BaseModel):
    id: int
    name: Optional[str] = Field(None, min_length=1, max_length=120)
    slug: Optional[str] = Field(None, min_length=1, max_length=80)
    category: Optional[str] = Field(None, min_length=1, max_length=30)
    provider: Optional[str] = Field(None, min_length=1, max_length=60)
    default_config: Optional[dict] = None
    is_active: Optional[bool] = None


class ServiceCatalogResponse(ServiceCatalogBase):
    id: int

    class Config:
        from_attributes = True
