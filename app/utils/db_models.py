import uuid

import sqlalchemy as sa
from omegaconf import OmegaConf
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.ext.declarative import declarative_base

import utils.pydantic_models as p_models


Base = declarative_base()

config = OmegaConf.load('config.yaml')


class UC(Base):
    __tablename__ = 'caso_uso'
    __table_args__ = {'schema': config.db.schema}
    id_caso_uso = sa.Column('id_caso_uso', UUID, primary_key=True, default=uuid.uuid4())
    nombre = sa.Column('nombre', sa.String())
    descripcion = sa.Column('descripcion', sa.String())
    lider = sa.Column('lider', sa.String())
    responsables = sa.Column('responsables', sa.String())

    @classmethod
    def from_pydantic(cls, pydantic_obj: p_models.UC):
        return cls(
            nombre=pydantic_obj.nombre,
            descripcion=pydantic_obj.descripcion,
            lider=pydantic_obj.lider,
            responsables=",".join(pydantic_obj.responsables)
        )


class DatasetRaw(Base):
    __tablename__ = 'ficheros_raw'
    __table_args__ = {'schema': config.db.schema}
    id_fichero = sa.Column('id_fichero', UUID, primary_key=True, default=uuid.uuid4())
    id_tipo_dataset = sa.Column('id_tipo_dataset', UUID)
    nombre = sa.Column('nombre', sa.String())
    ruta = sa.Column('ruta', sa.String())
    parametros = sa.Column('parametros', JSON)
    owner = sa.Column('owner', sa.String())


class DatasetType(Base):
    __tablename__ = 'tipos_datasets'
    __table_args__ = {'schema': config.db.schema}
    id_tipo_dataset = sa.Column('id_tipo_dataset', UUID, primary_key=True, default=uuid.uuid4())
    nombre = sa.Column('nombre', sa.String())
    parametros = sa.Column('parametros', JSON)

    @classmethod
    def from_pydantic(cls, pydantic_obj: p_models.DatasetType):
        return cls(
            nombre=pydantic_obj.nombre,
            parametros=pydantic_obj.parametros
        )


class AdminUser(Base):
    __tablename__ = 'admin_users'
    __table_args__ = {'schema': config.db.schema}
    id_usuario = sa.Column('id_usuario', UUID, primary_key=True, default=uuid.uuid4())
    nombre = sa.Column('nombre', sa.String())
    email = sa.Column('email', sa.String())
