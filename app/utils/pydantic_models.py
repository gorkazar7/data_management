from typing import Dict, Any, List

from pydantic import BaseModel


class DatasetType(BaseModel):
    nombre: str
    parametros: Dict[str, Any]


class FileMetadata(BaseModel):
    tipo_dataset: str
    owner: str
    parametros: Dict[str, Any]


class UC(BaseModel):
    nombre: str
    descripcion: str
    lider: str
    responsables: List[str]
